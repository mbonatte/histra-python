# Bugs found in the original C# code

These findings are limited to the C# files inspected for the translation comparison. The source appears decompiled, but the defects below are present in the reconstructed method bodies and are not merely local-variable naming artifacts.

## High confidence

### 1. Line-search resize branches dereference `null`

Affected files include Regula Falsi, Secant, Bisection, and Initial Interpolated searches.

Typical code:

```csharp
if (x.sz != dU.sz)
{
    x = null;
    x.CopyFrom(dU);
}
```

Example: `SolverRuntime.LineSearch/RegulaFalsiLineSearch.cs`, lines 29–33.

If the system dimension changes after `x` has already been allocated, `x.CopyFrom` throws `NullReferenceException`. The object should be recreated before copying.

### 2. `InitialInterpolatedSearch` hides instead of overrides base methods

`InitialInterpolatedSearch.cs`, lines 17 and 37, declares:

```csharp
internal new virtual int newStep(...)
internal new virtual int search(...)
```

The algorithm is held through a `LineSearch` reference. Because these methods hide rather than override the base virtual methods, normal virtual dispatch can call the base no-op implementation. The intended search may therefore never execute.

The Python revision implements it as a real polymorphic method.

### 3. Inconsistent line-search residual signs

`NewtonLineSearch.cs`, lines 43 and 52, defines both endpoint values as:

```csharp
s = -dU · R
```

But Regula Falsi, Secant, Bisection, and Initial Interpolated trial values use:

```csharp
s_j = +dU · R_j
```

For example, `RegulaFalsiLineSearch.cs`, line 97. This changes the sign of only the interior evaluations and can invalidate bracketing and secant updates.

The Python revision consistently uses `-dU · R`.

### 4. Standard method selection omits Initial Interpolated and duplicates Bisection

Both Newton loops test a list containing `StandardBisectionLineSearch` twice and omit `StandardInitialInterpolatedLineSearch`.

- `NewtonRaphson.cs`, line 23
- `NewtonLineSearch.cs`, line 31

As a result, Standard Initial Interpolated can behave like a Modified method by not updating tangent stiffness each iteration.

The Python revision treats every method whose name begins with `Standard` as Standard.

### 5. Force-based load discretization is unsafe for unloading

`LoadControl.cs`, lines 135–144, calculates the number of force steps from the signed multiplier difference:

```csharp
num6 = Convert.ToInt16((num4 - num3) / num5);
```

For a descending/cyclic load segment this can be negative or zero, producing a wrong step count or division by zero. The Python revision uses the absolute span to calculate a positive number of steps while retaining the signed increment.

### 6. `CTestNormUnbalance.getCopy()` returns the wrong convergence-test type

`CTestNormUnbalance.cs`, lines 41–44:

```csharp
return new CTestNormDispIncr(_tol, iterations, _nType);
```

It returns a displacement-increment test instead of a residual-force test. The third argument is also supplied in the `maxU` position, not the norm-type position.

The Python revision returns the same criterion and preserves `max_u`.

### 7. Left scalar multiplication returns the unscaled vector

`MatrixManager/Vector.cs`, lines 396–404, constructs a scaled vector but returns `v`:

```csharp
Vector vector = new Vector(v.sz);
...
return v;
```

Therefore `scalar * vector` yields the original vector. `vector * scalar` uses a different overload and appears correct.

### 8. Arc-length adaptive radius is reset at each new step

`ArcLength.domainChanged()` initializes `arcLength2` from `Analysis.Dr2` and `Commit()` adapts it. But `ArcLength.NewStep()`, line 155, assigns `arcLength2 = an.Dr2` again before every predictor. That largely defeats adaptation performed at the prior commit.

The Python revision initializes the radius on domain/segment initialization and preserves adapted values between steps.

### 9. Arc-length maximum-radius units are inconsistent

`ArcLength.Commit()`, lines 303–305, compares the squared quantity `arcLength2` directly with `MaxArcLengthRay` and then assigns the unsquared value to it. Elsewhere the code uses `sqrt(arcLength2)` as the radius.

The Python revision compares radius with radius and stores the squared limit.

## Medium confidence

### 10. Bisection early convergence during bracketing leaves `LS.X` as a correction

`BisectionLineSearch.cs`, lines 65–89, can return immediately when the bracketing trial satisfies tolerance. At that point the element state is at the full trial `eta`, but `LS.X` contains only `(eta - eta_previous) * dU`, not total `eta*dU`.

This does not affect force-residual convergence, but it can corrupt displacement-increment or work convergence tests. The Python revision always stores total `eta*dU` before returning.

## Not classified as a C# bug

The following Python issues were not defects in the C# source:

- cumulative displacement being cleared;
- initial stiffness always being assembled for Standard Newton;
- failed ALS starting from the failed full-step state;
- missing load-function item parsing;
- vector rollback calling the wrong overload;
- zero-diagonal DOFs being silently treated as supports;
- hard-coded graph load factor;
- Python nonlinear API returning success after failure.
