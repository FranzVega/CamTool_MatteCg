import maya.cmds as cmds
import re


def renameCamera(*args):
    """Renombra la cámara seleccionada basándose en el nombre de la escena y los frames"""
    selected_cameras = cmds.ls(selection=True)

    if not selected_cameras:
        cmds.confirmDialog(title='Set Camera', message='Please select a camera!', button=['OK'])
        return
    
    camera = selected_cameras[0]
    start_frame = cmds.playbackOptions(query=True, minTime=True)
    end_frame = cmds.playbackOptions(query=True, maxTime=True)
    scene_name = cmds.file(query=True, sceneName=True)
    
    pattern = re.compile(r"SH\d+_")
    match = pattern.search(scene_name)
    
    if match:
        new_name = "CAM_" + match.group() + "FR_" + str(int(start_frame)) + "_" + str(int(end_frame))
    else:
        pattern_numbers = re.compile(r"SH\d+[A-Za-z]+")
        match_numbers = pattern_numbers.search(scene_name)
        if match_numbers:
            new_name = "CAM_" + match_numbers.group() + "_FR_" + str(int(start_frame)) + "_" + str(int(end_frame))
        else:
            new_name = "CAM_FR_" + str(int(start_frame)) + "_" + str(int(end_frame))

    try:
        cmds.rename(camera, new_name)
        cmds.confirmDialog(title='Success', message=f'Camera renamed to: {new_name}', button=['OK'])
    except Exception as e:
        cmds.confirmDialog(title='Error', message=f'Could not rename camera: {str(e)}', button=['OK'])


def renameFrames(*args):
    """Renombra o agrega información de frames a la cámara seleccionada"""
    selected = cmds.ls(selection=True)
    
    if not selected:
        cmds.confirmDialog(title='Error', message='Please select a camera!', button=['OK'])
        return
    
    camera = selected[0]
    start_frame = int(cmds.playbackOptions(query=True, minTime=True))
    end_frame = int(cmds.playbackOptions(query=True, maxTime=True))
    
    # Buscar si ya tiene información de frames
    match = re.search(r"_FR_\d+_\d+", camera)
    
    if match:
        # Reemplazar los frames existentes
        new_name = re.sub(r"_FR_\d+_\d+", f"_FR_{start_frame}_{end_frame}", camera)
    else:
        # Agregar frames al final
        new_name = f"{camera}_FR_{start_frame}_{end_frame}"
    
    try:
        cmds.rename(camera, new_name)
        cmds.confirmDialog(title='Success', message=f'Camera renamed to: {new_name}', button=['OK'])
    except Exception as e:
        cmds.confirmDialog(title='Error', message=f'Could not rename camera: {str(e)}', button=['OK'])


def setRenderCam(*args):
    """Establece la cámara seleccionada como cámara de render"""
    selected = cmds.ls(selection=True, type='transform')
    
    if not selected:
        cmds.confirmDialog(title='Error', message='Please select a camera!', button=['OK'])
        return
    
    camera = selected[0]
    
    # Verificar si es una cámara
    shapes = cmds.listRelatives(camera, shapes=True, type='camera')
    if not shapes:
        cmds.confirmDialog(title='Error', message='Selected object is not a camera!', button=['OK'])
        return
    
    # Establecer como cámara de render
    cmds.lookThru(camera)
    panel = cmds.getPanel(withFocus=True)
    cmds.modelEditor(panel, edit=True, camera=camera)
    
    cmds.confirmDialog(title='Success', message=f'{camera} set as render camera', button=['OK'])


def setTimeSlider(*args):
    """Establece el time slider basándose en el nombre de la cámara seleccionada"""
    selected = cmds.ls(selection=True)
    
    if not selected:
        cmds.confirmDialog(title='Error', message='Please select a camera!', button=['OK'])
        return
    
    camera = selected[0]
    
    # Buscar los frames en el nombre de la cámara
    match = re.search(r"_FR_(\d+)_(\d+)", camera)
    
    if not match:
        cmds.confirmDialog(title='Error', message='Camera name does not contain frame information (_FR_START_END)', button=['OK'])
        return
    
    start_frame = int(match.group(1))
    end_frame = int(match.group(2))
    
    # Establecer el time slider
    cmds.playbackOptions(minTime=start_frame, maxTime=end_frame)
    cmds.playbackOptions(animationStartTime=start_frame, animationEndTime=end_frame)
    cmds.currentTime(start_frame)
    
    cmds.confirmDialog(title='Success', message=f'Time slider set to: {start_frame} - {end_frame}', button=['OK'])


def createUnrealCamera(*args):
    """Exporta la cámara seleccionada como FBX para Unreal Engine"""
    selected = cmds.ls(selection=True, type='transform')
    
    if not selected:
        cmds.confirmDialog(title='Error', message='Select a camera!', button=['OK'])
        return
    
    camera = selected[0]
    
    # Verificar que el nombre tenga el formato correcto con frames
    match = re.search(r"_FR_(\d+)_(\d+)", camera)
    
    if not match:
        cmds.confirmDialog(title='Error', message='Camera name must contain frame information (_FR_START_END)', button=['OK'])
        return
    
    start_frame = int(match.group(1))
    end_frame = int(match.group(2))
    
    # Obtener el path de la escena actual
    scene_path = cmds.file(query=True, sceneName=True)
    
    if not scene_path:
        cmds.confirmDialog(title='Error', message='Please save the scene first!', button=['OK'])
        return
    
    # Crear el path para el FBX
    import os
    scene_dir = os.path.dirname(scene_path)
    fbx_path = os.path.join(scene_dir, f"{camera}.fbx")
    
    # Seleccionar solo la cámara
    cmds.select(camera, replace=True)
    
    # Configurar opciones de exportación FBX
    cmds.loadPlugin('fbxmaya', quiet=True)
    
    # Exportar FBX
    try:
        cmds.file(fbx_path, force=True, options="v=0", type="FBX export", 
                  preserveReferences=True, exportSelected=True)
        cmds.confirmDialog(title='Success', message=f'Camera exported to:\n{fbx_path}', button=['OK'])
    except Exception as e:
        cmds.confirmDialog(title='Error', message=f'Export failed:\n{str(e)}', button=['OK'])


def main():
    """Función principal que crea la interfaz de usuario"""
    # Evitar ventanas duplicadas
    if cmds.window("camToolsWin", exists=True):
        cmds.deleteUI("camToolsWin")

    window = cmds.window("camToolsWin", title='CamTools version mattecg 3.0', iconName='CamTools', widthHeight=(300, 400))
    cmds.columnLayout(adj=1)
    cmds.text(label='Choose an option', w=300, h=30)
    cmds.separator()

    cmds.button(label='Rename Camera', w=300, h=50, c=renameCamera)
    cmds.separator()
    cmds.button(label='Rename/Add Frames', w=300, h=50, c=renameFrames)
    cmds.separator()
    cmds.button(label='Set Render Cam', w=300, h=50, c=setRenderCam)
    cmds.separator()
    cmds.button(label='Set Time Slider', w=300, h=50, c=setTimeSlider)
    cmds.separator()
    cmds.button(label='Export Unreal Engine Camera', w=300, h=50, c=createUnrealCamera)
    cmds.separator()
    cmds.text(label='Created by Franz Vega', font="smallObliqueLabelFont", align="right")

    cmds.showWindow(window)