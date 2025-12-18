import maya.cmds as cmds
import re
import os
import sys

# CONFIGURACIÓN DE VERSIÓN Y ACTUALIZACIÓN
__version__ = "2.0.0"  # Versión actual del script
GITHUB_VERSION_URL = "https://github.com/FranzVega/CamTool_MatteCg/blob/main/version.json"
GITHUB_SCRIPT_URL = "https://github.com/FranzVega/CamTool_MatteCg/blob/main/source/CamTools.py"


def check_for_updates():
    """Verifica si hay una nueva versión disponible en GitHub"""
    try:
        # Intentar importar urllib (Python 2 y 3 compatible)
        try:
            from urllib.request import urlopen  # Python 3
        except ImportError:
            from urllib2 import urlopen  # Python 2
        
        import json
        
        # Descargar información de versión
        response = urlopen(GITHUB_VERSION_URL, timeout=5)
        version_data = json.loads(response.read().decode('utf-8'))
        
        latest_version = version_data.get("version", "0.0.0")
        changelog = version_data.get("changelog", "No changelog available")
        
        # Comparar versiones
        if compare_versions(latest_version, __version__) > 0:
            return {
                "update_available": True,
                "latest_version": latest_version,
                "current_version": __version__,
                "changelog": changelog
            }
        else:
            return {
                "update_available": False,
                "latest_version": latest_version,
                "current_version": __version__
            }
    
    except Exception as e:
        print(f"Error checking for updates: {str(e)}")
        return None


def compare_versions(version1, version2):
    """
    Compara dos versiones en formato X.Y.Z
    Retorna: 1 si version1 > version2, -1 si version1 < version2, 0 si son iguales
    """
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    
    for i in range(max(len(v1_parts), len(v2_parts))):
        v1 = v1_parts[i] if i < len(v1_parts) else 0
        v2 = v2_parts[i] if i < len(v2_parts) else 0
        
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
    
    return 0


def download_update():
    """Descarga e instala la actualización desde GitHub"""
    try:
        # Intentar importar urllib (Python 2 y 3 compatible)
        try:
            from urllib.request import urlopen  # Python 3
        except ImportError:
            from urllib2 import urlopen  # Python 2
        
        # Descargar el nuevo script
        response = urlopen(GITHUB_SCRIPT_URL, timeout=10)
        new_script_content = response.read().decode('utf-8')
        
        # Obtener la ruta del script actual
        current_script_path = __file__
        backup_path = current_script_path + ".backup"
        
        # Crear backup del script actual
        with open(current_script_path, 'r') as f:
            current_content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(current_content)
        
        # Escribir el nuevo script
        with open(current_script_path, 'w') as f:
            f.write(new_script_content)
        
        return True, "Update successful! Please restart Maya or reload the script."
    
    except Exception as e:
        # Si algo sale mal, restaurar el backup
        try:
            if os.path.exists(backup_path):
                with open(backup_path, 'r') as f:
                    backup_content = f.read()
                with open(current_script_path, 'w') as f:
                    f.write(backup_content)
        except:
            pass
        
        return False, f"Update failed: {str(e)}"


def show_update_dialog(update_info):
    """Muestra un diálogo con información de actualización"""
    if update_info is None:
        cmds.confirmDialog(
            title='Update Check',
            message='Could not check for updates. Please check your internet connection.',
            button=['OK'],
            defaultButton='OK'
        )
        return
    
    if not update_info["update_available"]:
        cmds.confirmDialog(
            title='No Updates',
            message=f'You are using the latest version ({__version__})',
            button=['OK'],
            defaultButton='OK'
        )
        return
    
    # Hay actualización disponible
    message = f'New version available!\n\n'
    message += f'Current version: {update_info["current_version"]}\n'
    message += f'Latest version: {update_info["latest_version"]}\n\n'
    message += f'Changelog:\n{update_info["changelog"]}\n\n'
    message += f'Do you want to update now?'
    
    result = cmds.confirmDialog(
        title='Update Available',
        message=message,
        button=['Update Now', 'Later'],
        defaultButton='Update Now',
        cancelButton='Later',
        dismissString='Later'
    )
    
    if result == 'Update Now':
        success, msg = download_update()
        cmds.confirmDialog(
            title='Update Status',
            message=msg,
            button=['OK']
        )
        
        if success:
            # Recargar el módulo
            try:
                import importlib
                importlib.reload(sys.modules[__name__])
                cmds.warning("Script updated! Reopening window...")
                main()
            except:
                pass


def check_updates_menu(*args):
    """Función para el botón de verificar actualizaciones"""
    update_info = check_for_updates()
    show_update_dialog(update_info)


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
    
    match = re.search(r"_FR_\d+_\d+", camera)
    
    if match:
        new_name = re.sub(r"_FR_\d+_\d+", f"_FR_{start_frame}_{end_frame}", camera)
    else:
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
    shapes = cmds.listRelatives(camera, shapes=True, type='camera')
    
    if not shapes:
        cmds.confirmDialog(title='Error', message='Selected object is not a camera!', button=['OK'])
        return
    
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
    match = re.search(r"_FR_(\d+)_(\d+)", camera)
    
    if not match:
        cmds.confirmDialog(title='Error', message='Camera name does not contain frame information (_FR_START_END)', button=['OK'])
        return
    
    start_frame = int(match.group(1))
    end_frame = int(match.group(2))
    
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
    match = re.search(r"_FR_(\d+)_(\d+)", camera)
    
    if not match:
        cmds.confirmDialog(title='Error', message='Camera name must contain frame information (_FR_START_END)', button=['OK'])
        return
    
    start_frame = int(match.group(1))
    end_frame = int(match.group(2))
    
    scene_path = cmds.file(query=True, sceneName=True)
    
    if not scene_path:
        cmds.confirmDialog(title='Error', message='Please save the scene first!', button=['OK'])
        return
    
    scene_dir = os.path.dirname(scene_path)
    fbx_path = os.path.join(scene_dir, f"{camera}.fbx")
    
    cmds.select(camera, replace=True)
    cmds.loadPlugin('fbxmaya', quiet=True)
    
    try:
        cmds.file(fbx_path, force=True, options="v=0", type="FBX export", 
                  preserveReferences=True, exportSelected=True)
        cmds.confirmDialog(title='Success', message=f'Camera exported to:\n{fbx_path}', button=['OK'])
    except Exception as e:
        cmds.confirmDialog(title='Error', message=f'Export failed:\n{str(e)}', button=['OK'])


def main():
    """Función principal que crea la interfaz de usuario"""
    # Verificar actualizaciones al abrir (opcional, puedes comentar esta línea)
    update_info = check_for_updates()
    if update_info and update_info["update_available"]:
        # Mostrar notificación sutil en lugar de diálogo
        cmds.warning(f"CamTools: New version {update_info['latest_version']} available! Check 'About/Updates' menu.")
    
    # Evitar ventanas duplicadas
    if cmds.window("camToolsWin", exists=True):
        cmds.deleteUI("camToolsWin")

    window = cmds.window("camToolsWin", title=f'CamTools v{__version__}', iconName='CamTools', widthHeight=(300, 450))
    
    # Layout principal
    main_layout = cmds.columnLayout(adj=1)
    
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
    cmds.button(label='Create Unreal Engine Camera', w=300, h=50, c=createUnrealCamera)
    cmds.separator(height=20)
    
    # Botón de actualización
    cmds.button(label='Check for Updates', w=300, h=30, 
                backgroundColor=[0.3, 0.5, 0.7], c=check_updates_menu)
    cmds.separator()
    
    cmds.text(label=f'v{__version__} - Created for MatteCG by Franz Vega', 
              font="smallObliqueLabelFont", align="right")

    cmds.showWindow(window)
