# 3D view of the officeComfort results. Run from the case folder:
#     paraview --script=view_room.py
from paraview.simple import *
import os

foam = os.path.join(os.getcwd(), 'office.foam')
open(foam, 'a').close()
view = GetActiveViewOrCreate('RenderView')

# Air inside the room, at the last saved iteration
air = OpenFOAMReader(registrationName='air', FileName=foam)
air.MeshRegions = ['internalMesh']
air.UpdatePipelineInformation()
try:
    times = list(air.TimestepValues)
except TypeError:
    times = [air.TimestepValues]
scene = GetAnimationScene()
scene.UpdateAnimationUsingDataTimeSteps()
scene.AnimationTime = times[-1]
regions = list(air.GetProperty('MeshRegions').Available)

def patches(names, color, opacity=1.0):
    """Show the room patches whose name contains one of names"""
    sel = [r for r in regions if any(n in r for n in names)]
    src = OpenFOAMReader(registrationName=names[0], FileName=foam)
    src.MeshRegions = sel
    d = Show(src, view)
    ColorBy(d, None)
    d.AmbientColor = d.DiffuseColor = color
    d.Opacity = opacity
    return src

patches(['floor'], [0.75, 0.75, 0.75])
patches(['person'], [0.95, 0.6, 0.35])
patches(['desk'], [0.6, 0.45, 0.3])
patches(['pc'], [0.2, 0.2, 0.2])
patches(['lights'], [1.0, 1.0, 0.6])
patches(['supply'], [0.1, 0.3, 1.0])
patches(['return'], [0.6, 0.1, 0.1])
patches(['window'], [0.6, 0.85, 1.0], 0.35)
Show(Outline(registrationName='room outline', Input=air), view)

# Temperature in degC
airC = Calculator(registrationName='air degC', Input=air)
airC.AttributeType = 'Point Data'
airC.ResultArrayName = 'T_degC'
airC.Function = 'T-273.15'

def slice(name, field, origin, normal, visible):
    s = Slice(registrationName=name, Input=airC)
    s.SliceType = 'Plane'
    s.SliceType.Origin = origin
    s.SliceType.Normal = normal
    d = Show(s, view)
    ColorBy(d, ('POINTS', field))
    if not visible:
        Hide(s, view)
    return s

# Toggle these with the eye icons in the Pipeline Browser
slice('PMV at 1.1 m (neck)', 'PMV', [2.5, 2.0, 1.1], [0, 0, 1], True)
slice('PMV at 0.6 m (waist)', 'PMV', [2.5, 2.0, 0.6], [0, 0, 1], False)
slice('PMV at 0.1 m (ankles)', 'PMV', [2.5, 2.0, 0.1], [0, 0, 1], False)
slice('DR at 1.1 m', 'DR', [2.5, 2.0, 1.1], [0, 0, 1], False)
slice('T section through diffuser', 'T_degC', [2.5, 2.0, 1.4], [1, 0, 0],
      False)

# Air paths from the ceiling diffuser
paths = StreamTracer(registrationName='air paths from diffuser', Input=air,
                     SeedType='Point Cloud')
paths.Vectors = ['POINTS', 'U']
paths.IntegrationDirection = 'FORWARD'
paths.MaximumStreamlineLength = 30.0
paths.SeedType.Center = [2.5, 2.0, 2.76]
paths.SeedType.Radius = 0.25
paths.SeedType.NumberOfPoints = 300
d = Show(paths, view)
ColorBy(d, ('POINTS', 'U', 'Magnitude'))

# Colour scales, set after colouring so they are not rescaled
def lut(field, preset, lo, hi, title, fmt, corner, visible):
    f = GetColorTransferFunction(field)
    f.ApplyPreset(preset, True)
    f.AutomaticRescaleRangeMode = 'Never'
    f.RescaleTransferFunction(lo, hi)
    bar = GetScalarBar(f, view)
    bar.Title = title
    bar.ComponentTitle = ''
    bar.HorizontalTitle = 1
    bar.TitleFontSize = 14
    bar.LabelFontSize = 12
    bar.ScalarBarLength = 0.3
    bar.AutomaticLabelFormat = 0
    bar.LabelFormat = bar.RangeLabelFormat = fmt
    bar.Visibility = visible
    for loc in (corner, corner.replace(' ', '')):
        try:
            bar.WindowLocation = loc
            break
        except Exception:
            pass

# Show a hidden slice's colour legend with the "Toggle Color Legend" button
lut('PMV', 'Cool to Warm', -0.7, 0.7, 'PMV', '%.1f', 'Upper Right Corner', 1)
lut('U', 'Viridis (matplotlib)', 0.0, 0.5, '|U| [m/s]', '%.2f',
    'Lower Right Corner', 1)
lut('DR', 'Inferno (matplotlib)', 0.0, 20.0, 'DR [%]', '%.0f',
    'Upper Left Corner', 0)
lut('T_degC', 'Jet', 20.0, 26.0, 'T [degC]', '%.0f', 'Lower Left Corner', 0)

# Looking into the room from outside the window
view.CameraPosition = [-3.0, -6.0, 6.5]
view.CameraFocalPoint = [2.5, 2.0, 1.0]
view.CameraViewUp = [0, 0, 1]
view.ResetCamera(False)
Render(view)
