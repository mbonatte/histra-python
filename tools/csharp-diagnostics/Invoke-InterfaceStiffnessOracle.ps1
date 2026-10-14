param([Parameter(Mandatory=$true)][string]$InstalledRoot,
      [Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference='Stop'
foreach($name in @('MonoGame.Framework.dll','XNALibrary.dll','UtilityLibrary.dll','SirioCommon.dll','MatrixManager.dll','ModelLibrary.dll')) {
    [void][Reflection.Assembly]::LoadFrom((Join-Path $InstalledRoot $name))
}
function SetInterface($obj,$name,$value) {[Objects.Interface].GetProperty($name).SetValue($obj,$value,$null)}
function MatrixRows($m,$size) {
    $rows=@()
    for($r=0;$r -lt $size;$r++) {
        $row=@();for($c=0;$c -lt $size;$c++) {$row += $m.Read($r,$c)}
        $rows += ,$row
    }
    return ,$rows
}
$output=@()
foreach($constrained in @($false,$true)) {foreach($uniform in @($false,$true)) {foreach($alpha in @(0.0,0.37,1.0)) {
    $intf=[Activator]::CreateInstance([Objects.Interface])
    SetInterface $intf 'Nrow' ([int]2);SetInterface $intf 'Ncol' ([int]3)
    SetInterface $intf 'Ngroup' ([int]1)
    SetInterface $intf 'Length' ([double]2.718281828459045)
    SetInterface $intf 'Thickness' ([double[]]@(0.48,0.66))
    SetInterface $intf 'DimAff' ([int[]]@(6,2,4))
    $pt=if($constrained){[UtilityLibrary.Tipi.ElementTypeEnum]::Restraint}else{[UtilityLibrary.Tipi.ElementTypeEnum]::Quad}
    SetInterface $intf 'ParentTypeElement1' $pt
    SetInterface $intf 'ParentTypeElement2' ([UtilityLibrary.Tipi.ElementTypeEnum]::Quad)
    $vertices=[Microsoft.Xna.Framework.Vector2[]]@(
        [Microsoft.Xna.Framework.Vector2]::new([single]0.,[single]-.31),
        [Microsoft.Xna.Framework.Vector2]::new([single]2.7,[single]-.22),
        [Microsoft.Xna.Framework.Vector2]::new([single]2.4,[single].44),
        [Microsoft.Xna.Framework.Vector2]::new([single].05,[single].36))
    SetInterface $intf 'VInt2D' $vertices
    $fibres=[Activator]::CreateInstance([Collections.Generic.List[Objects.Spring]])
    $ks=@();$kts=@()
    for($j=0;$j -lt 6;$j++) {
        $s=[Activator]::CreateInstance([Objects.SpringHysteretic])
        $s.K=137.56;if(-not $uniform){$s.K += $j*.273435095827634}
        $s.K_tang=$s.K*.137656839215837
        $ks += $s.K;$kts += $s.K_tang;$fibres.Add($s)
    }
    SetInterface $intf 'Trasv_1' $fibres
    foreach($name in @('Slid','SlidOutPlan')) {
        $list=[Activator]::CreateInstance([Collections.Generic.List[Objects.Spring]])
        $count=if($name -eq 'Slid'){1}else{2}
        for($j=0;$j -lt $count;$j++) {$s=[Activator]::CreateInstance([Objects.SpringLinearElastic]);$s.K=37.219+$j*.19;$list.Add($s)}
        SetInterface $intf $name $list
    }
    $state=[Objects.InterfaceState].GetConstructor([Type[]]@([Objects.Interface],[bool])).Invoke([object[]]@($intf,$false))
    SetInterface $intf 'Status' $state
    [void][Objects.Interface].GetMethod('ComputeK').Invoke($intf,[object[]]@([double]$alpha))
    $xy=@();foreach($p in $vertices){$xy += ,@([double]$p.X,[double]$p.Y)}
    $output += @{constrained=$constrained;uniform=$uniform;alpha=$alpha;length=2.718281828459045;thickness=@(.48,.66);vertices=$xy;spring_k=$ks;spring_kt=$kts;
        K=(MatrixRows $state.K 6);Kslid=(MatrixRows $state.Kslid 2);Kout=(MatrixRows $state.KslidOutPlan 4)}
}}}
@{source='Original Interface.ComputeK: transverse, in-plane and out-of-plane stiffness blocks';cases=$output} |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
