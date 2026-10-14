param([Parameter(Mandatory=$true)][string]$ModelPath,[Parameter(Mandatory=$true)][string]$OutputDirectory,[string]$InstallDirectory='C:\Program Files\Gruppo Sismica\HiStrA Bridges 2026.1.1')
$ErrorActionPreference='Stop'
$a=[IO.Path]::GetFullPath($OutputDirectory);$i=$InstallDirectory
[void][IO.Directory]::CreateDirectory($a)
foreach($name in @('MonoGame.Framework.dll','XNALibrary.dll','UtilityLibrary.dll','SirioCommon.dll','MatrixManager.dll','ModelLibrary.dll','SolverRuntime.dll')) {[void][Reflection.Assembly]::LoadFrom((Join-Path $i $name))}
$ctor=[ModelLibrary.Model].GetConstructors()|Where-Object{$_.GetParameters().Length -eq 2}|Select-Object -First 1
$model=$ctor.Invoke([object[]]@([enum]::Parse($ctor.GetParameters()[0].ParameterType,'RailBridge'),$false))
$path=[IO.Path]::GetFullPath($ModelPath)
[void][SirioSoft.SerializeXmlReader].GetMethod('ReadFromFile',[Type[]]@([string],[string],[object])).Invoke($null,[object[]]@([string]$path,[string]'HiStrA',$model))
[ModelLibrary.Model].GetField('_model',[Reflection.BindingFlags]'Static,NonPublic').SetValue($null,$model)
$model.IsLocked=$false
$p=[Activator]::CreateInstance([SolverRuntime.Program])
[SolverRuntime.Program].GetField('_LS',[Reflection.BindingFlags]'Instance,NonPublic,Public').SetValue($p,[Activator]::CreateInstance([MatrixManager.LinearSystem]))
Write-Output 'Calling original material extraction, geometry and interface generation'
[ModelManagement.ComputationalElementsOperations.ConstitutiveLawOperations]::ExtractInfoFromMaterials($model.Collections)
[void][SolverRuntime.ModelManager].GetMethod('PreliminaryOperations',[Reflection.BindingFlags]'Static,NonPublic').Invoke($null,@())
[ModelManagement.ComputationalElementsOperations.InterfaceOperations]::GenerateInterfaces($model)
Write-Output ('Generated '+$model.Collections.Quads.Count+' quads; '+$model.Collections.Interfaces.Count+' interfaces')
$rows=[Collections.Generic.List[object]]::new()
foreach($entry in $model.Collections.Quads.Collection.GetEnumerator()) {
 $q=$entry.Value;$rows.Add(@{family='Quad';key=$entry.Key;node_keys=@($q.NodeKeys);Length=@($q.Length);Diago=@($q.Diago);Cos=@($q.Cos);Sin=@($q.Sin);thickness=@($q.Thickness|ForEach-Object{[double]$_});K=$q.Spring.K;Fy=$q.Spring.Fy;Area=$q.Spring.Area;Ur=$q.Spring.Ur})
}
foreach($entry in $model.Collections.Interfaces.Collection.GetEnumerator()) {
 $iface=$entry.Value;$group=[Objects.Interface].GetProperty('Trasv_1').GetValue($iface,$null)
 for($j=0;$j -lt $group.Count;$j++) {
  $spring=$group[$j]
  $rows.Add(@{family='Interface';key=$entry.Key;geometry=@([string]([Objects.Interface].GetProperty('ParentTypeElement1').GetValue($iface,$null)),([Objects.Interface].GetProperty('ParentElementKey1').GetValue($iface,$null)),([Objects.Interface].GetProperty('Face1').GetValue($iface,$null)),[string]([Objects.Interface].GetProperty('ParentTypeElement2').GetValue($iface,$null)),([Objects.Interface].GetProperty('ParentElementKey2').GetValue($iface,$null)),([Objects.Interface].GetProperty('Face2').GetValue($iface,$null)));node_keys=@(([Objects.Interface].GetProperty('NodeKeys').GetValue($iface,$null)));index=$j;K=$spring.K;Area=$spring.Area;Fy=$spring.Fy;Ur=$spring.Ur;E3p=$spring.E3p})
 }
}
$rows|ConvertTo-Json -Depth 6|Set-Content (Join-Path $a 'native-generated-spring-definitions.json') -Encoding UTF8
