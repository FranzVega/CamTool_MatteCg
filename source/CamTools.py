# -*- coding: utf-8 -*-

import maya.cmds as cmds

import re

import os

import sys



# CONFIGURACION DE VERSION Y ACTUALIZACION

__version__ = "2.1.0"  # Version actual del script

GITHUB_VERSION_URL = "https://raw.githubusercontent.com/FranzVega/CamTool_MatteCg/main/version.json"

GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/FranzVega/CamTool_MatteCg/main/source/CamTools.py"





def check_for_updates():

    """Verifica si hay una nueva version disponible en GitHub"""

    try:

        # Intentar importar urllib (Python 2 y 3 compatible)

        try:

            from urllib.request import urlopen  # Python 3

        except ImportError:

            from urllib2 import urlopen  # Python 2

        

        import json

        

        # Descargar informacion de version

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

        print("Error checking for updates: {0}".format(str(e)))

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

    """Descarga e instala la actualizacion desde GitHub"""

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

        

        # Crear backup del script actual con encoding UTF-8

        try:

            with open(current_script_path, 'r', encoding='utf-8') as f:

                current_content = f.read()

        except TypeError:

            # Python 2 no soporta el parametro encoding directamente

            import io

            with io.open(current_script_path, 'r', encoding='utf-8') as f:

                current_content = f.read()

        

        try:

            with open(backup_path, 'w', encoding='utf-8') as f:

                f.write(current_content)

        except TypeError:

            import io

            with io.open(backup_path, 'w', encoding='utf-8') as f:

                f.write(current_content)

        

        # Escribir el nuevo script con encoding UTF-8

        try:

            with open(current_script_path, 'w', encoding='utf-8') as f:

                f.write(new_script_content)

        except TypeError:

            import io

            with io.open(current_script_path, 'w', encoding='utf-8') as f:

                f.write(new_script_content)

        

        return True, "Update successful! Please restart Maya or reload the script."

    

    except Exception as e:

        # Si algo sale mal, restaurar el backup

        try:

            if os.path.exists(backup_path):

                try:

                    with open(backup_path, 'r', encoding='utf-8') as f:

                        backup_content = f.read()

                    with open(current_script_path, 'w', encoding='utf-8') as f:

                        f.write(backup_content)

                except TypeError:

                    import io

                    with io.open(backup_path, 'r', encoding='utf-8') as f:

                        backup_content = f.read()

                    with io.open(current_script_path, 'w', encoding='utf-8') as f:

                        f.write(backup_content)

        except:

            pass

        

        return False, "Update failed: {0}".format(str(e))





def show_update_dialog(update_info):

    """Muestra un dialogo con informacion de actualizacion"""

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

            message='You are using the latest version ({0})'.format(__version__),

            button=['OK'],

            defaultButton='OK'

        )

        return

    

    # Hay actualizacion disponible

    message = 'New version available!\n\n'

    message += 'Current version: {0}\n'.format(update_info["current_version"])

    message += 'Latest version: {0}\n\n'.format(update_info["latest_version"])

    message += 'Changelog:\n{0}\n\n'.format(update_info["changelog"])

    message += 'Do you want to update now?'

    

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

            # Recargar el modulo

            try:

                import importlib

                importlib.reload(sys.modules[__name__])

                cmds.warning("Script updated! Reopening window...")

                main()

            except:

                pass





def check_updates_menu(*args):

    """Funcion para el boton de verificar actualizaciones"""

    update_info = check_for_updates()

    show_update_dialog(update_info)





def renameCamera(*args):

    # Obtener la camara seleccionada en la escena
    selected_cameras = cmds.ls(selection=True)

    # Verificar si hay alguna camara seleccionada
    if len(selected_cameras) == 0:
        # Terminar o lanzar un error si no hay ninguna camara seleccionada
        result = cmds.confirmDialog(title='Set Camera', message='Please select a camera!', button=['OK'], dismissString='OK')
    else:
        # Si hay una camara seleccionada, obtener el nombre de la camara
        camera = selected_cameras[0]

    # obtener el primer y ultimo fotograma de la linea de tiempo
    start_frame = cmds.playbackOptions(query=True, minTime=True)
    end_frame = cmds.playbackOptions(query=True, maxTime=True)

    # obtener el nombre de la escena actual en Maya
    scene_name = cmds.file(query=True, sceneName=True)
    
    # buscar el patron _SH\d+_ en el nombre de la escena
    pattern = re.compile(r"SH\d+_")
    match = pattern.search(scene_name)
    
    if match:
        # crear el nuevo nombre de la camara con el rango de fotogramas y el patron _SH001_ encontrado en la escena
        new_name = "CAM_" + match.group() + "FR_" + str(int(start_frame)) + "_" + str(int(end_frame))
    else:
        pattern_numbers = re.compile(r"SH\d+[A-Za-z]+")
        match_numbers = pattern_numbers.search(scene_name)
        if match_numbers:
            new_name = "CAM_" + match_numbers.group() + "_FR_" + str(int(start_frame)) + "_" + str(int(end_frame))
        else:
            # crear el nuevo nombre de la camara con el rango de fotogramas sin incluir el patron
            new_name = "CAM_FR_" + str(int(start_frame)) + "_" + str(int(end_frame))

    # renombrar la camara con el nuevo nombre
    cmds.rename(camera, new_name)
        
   # print("Rename Camera");





def renameFrames(*args):

     # Obtener la camara seleccionada en la escena
    selected_cameras = cmds.ls(selection=True)

    # Verificar si hay alguna camara seleccionada
    if len(selected_cameras) == 0:
        # Terminar o lanzar un error si no hay ninguna camara seleccionada
        result = cmds.confirmDialog(title='Set Camera', message='Please select a camera!', button=['OK'], dismissString='OK')
    else:
        # Si hay una camara seleccionada, obtener el nombre de la camara
        camera = selected_cameras[0]

    # obtener el primer y ultimo fotograma de la linea de tiempo
    start_frame = cmds.playbackOptions(query=True, minTime=True)
    end_frame = cmds.playbackOptions(query=True, maxTime=True)

    # buscar el patron "_X_Y" en el nombre de la camara
    pattern = re.compile(r"_\d+_\d+")
    match = pattern.search(camera)

    if match:
        # reemplazar el rango de fotogramas en el nombre de la camara por el nuevo rango de fotogramas de la linea de tiempo
        new_name = pattern.sub("_" + str(int(start_frame)) + "_" + str(int(end_frame)), camera)
        cmds.rename(camera, new_name)
    else:
        # renombrar la camara con el rango de fotogramas
        new_name = camera + "_" + str(int(start_frame)) + "_" + str(int(end_frame))
        cmds.rename(camera, new_name)    
    
   # print("Rename/Add Frames");




def setRenderCam(*args):

    # Obtener la camara seleccionada en la escena
    selected_cameras = cmds.ls(selection=True)

    # Verificar si hay alguna camara seleccionada
    if len(selected_cameras) == 0:
        # Terminar o lanzar un error si no hay ninguna camara seleccionada
        result = cmds.confirmDialog(title='Set Camera', message='Please select a camera!', button=['OK'], dismissString='OK')
    else:
        # Si hay una camara seleccionada, obtener el nombre de la camara
        camera = selected_cameras[0]
    
    # Verificar si el nombre de la camara cumple con el patron esperado
    if re.match(r".*_\d+_\d+.*", camera) is None:
        # Terminar o lanzar un error si el nombre de la camara no cumple con el patron
        result = cmds.confirmDialog(title='Set Camera', message='Incorrect Camera Name', button=['OK'], dismissString='OK')    
        
    else:
        # Si el nombre de la camara es valido, extraer el rango de fotograma
        frame_range_match = re.match(r".*_(\d+)_(\d+).*", camera)
        start_frame = int(frame_range_match.group(1))
        end_frame = int(frame_range_match.group(2))
        # Configurar el rango de fotogramas en el time slider
        cmds.playbackOptions(min=start_frame, max=end_frame)

        # Configurar el rango de fotogramas en los ajustes de render
        cmds.setAttr("defaultRenderGlobals.startFrame", start_frame)
        cmds.setAttr("defaultRenderGlobals.endFrame", end_frame)

        # Configurar la camara como la camara de render
        cmds.setAttr(camera + ".renderable", True)
    

   # cmds.lookThru(camera)

   # panel = cmds.getPanel(withFocus=True)

   # cmds.modelEditor(panel, edit=True, camera=camera)

    

    #cmds.confirmDialog(title='Success', message='{0} set as render camera'.format(camera), button=['OK'])





def setTimeSlider(*args):

     # Obtener la camara seleccionada en la escena
    selected_cameras = cmds.ls(selection=True)

    # Verificar si hay alguna camara seleccionada
    if len(selected_cameras) == 0:
        # Terminar o lanzar un error si no hay ninguna camara seleccionada
        result = cmds.confirmDialog(title='Set Camera', message='Please select a camera!', button=['OK'], dismissString='OK')
    else:
        # Si hay una camara seleccionada, obtener el nombre de la camara
        camera = selected_cameras[0]
    
    # Verificar si el nombre de la camara cumple con el patron esperado
    if re.match(r".*_\d+_\d+.*", camera) is None:
        # Terminar o lanzar un error si el nombre de la camara no cumple con el patron
        result = cmds.confirmDialog(title='Set Camera', message='Incorrect Camera Name', button=['OK'], dismissString='OK')    
        
    else:
        # Si el nombre de la camara es valido, extraer el rango de fotograma
        frame_range_match = re.match(r".*_(\d+)_(\d+).*", camera)
        start_frame = int(frame_range_match.group(1))
        end_frame = int(frame_range_match.group(2))
        # Configurar el rango de fotogramas en el time slider
        cmds.playbackOptions(min=start_frame, max=end_frame)

        # Configurar el rango de fotogramas en los ajustes de render
        cmds.setAttr("defaultRenderGlobals.startFrame", start_frame)
        cmds.setAttr("defaultRenderGlobals.endFrame", end_frame)

        # Configurar la camara como la camara de render
        cmds.setAttr(camera + ".renderable", True)  
    

    #cmds.confirmDialog(title='Success', message='Time slider set to: {0} - {1}'.format(start_frame, end_frame), button=['OK'])





def createUnrealCamera(*args):

    # === 0. Verificar camara seleccionada ===
    selected_cameras = cmds.ls(selection=True)
    
    if len(selected_cameras) == 0:
        cmds.confirmDialog(title='Set Camera', message='¡Por favor, selecciona una camara!', button=['OK'], dismissString='OK')
        raise Exception("No hay camara seleccionada")
    
    camera = selected_cameras[0]
    
    # Validar el nombre con el patron deseado
    if re.match(r".*_\d+_\d+.*", camera) is None:
        cmds.confirmDialog(title='Set Camera', message='Nombre de camara incorrecto', button=['OK'], dismissString='OK')
        raise Exception("Nombre de camara no valido")
    else:
            # Si el nombre de la camara es valido, extraer el rango de fotograma
            frame_range_match = re.match(r".*_(\d+)_(\d+).*", camera)
            start_frame = int(frame_range_match.group(1))
            end_frame = int(frame_range_match.group(2))
            # Configurar el rango de fotogramas en el time slider y la animacion completa
            cmds.playbackOptions(min=start_frame, max=end_frame)
            cmds.playbackOptions(animationStartTime=start_frame, animationEndTime=end_frame)
    
    
    # === 1. Crear nueva camara y copiar posicion ===
    camera_transform = cmds.xform(camera, query=True, matrix=True, worldSpace=True)
    new_camera = cmds.camera()
    new_camera_transform = new_camera[0]  # el transform de la camara
    new_camera_shape = new_camera[1]      # el shape de la camara
    
    # Renombrar camara nueva
    new_camera_name = cmds.rename(new_camera_transform, "UE_" + camera)
    new_camera_shape_name = cmds.listRelatives(new_camera_name, shapes=True)[0]
    
    # Aplicar transform de la camara original
    cmds.xform(new_camera_name, matrix=camera_transform, worldSpace=True)
    
    # === 2. Copiar focal length y animacion si hay ===
    focal_length_attr = camera + '.focalLength'
    new_focal_length_attr = new_camera_shape_name + '.focalLength'
    
    if cmds.objExists(focal_length_attr) and cmds.objExists(new_focal_length_attr):
        anim_keys = cmds.keyframe(focal_length_attr, query=True, timeChange=True)
        if anim_keys:
            for frame in anim_keys:
                value = cmds.getAttr(focal_length_attr, time=frame)
                cmds.setKeyframe(new_focal_length_attr, time=frame, value=value)
        else:
            value = cmds.getAttr(focal_length_attr)
            cmds.setAttr(new_focal_length_attr, value)
    
    # === 3. Parent constraint y bake ===
    constraint = cmds.parentConstraint(camera, new_camera_name, maintainOffset=True)[0]
    
    # Bake animation
    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)
    cmds.bakeResults(new_camera_name,
                     simulation=True,
                     t=(start_frame, end_frame),
                     at=['translate', 'rotate'],
                     preserveOutsideKeys=True)
    
    # Eliminar constraint
    cmds.delete(constraint)
    





def main():

    """Funcion principal que crea la interfaz de usuario"""

    # Verificar actualizaciones al abrir (opcional, puedes comentar esta linea)

    update_info = check_for_updates()

    if update_info and update_info["update_available"]:

        # Mostrar notificacion sutil en lugar de dialogo

        cmds.warning("CamTools: New version {0} available! Check 'Check for Updates' button.".format(update_info['latest_version']))

    

    # Evitar ventanas duplicadas

    if cmds.window("camToolsWin", exists=True):

        cmds.deleteUI("camToolsWin")



    window = cmds.window("camToolsWin", title='CamTools v{0}'.format(__version__), iconName='CamTools', widthHeight=(300, 450))

    

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

    

    # Boton de actualizacion

    cmds.button(label='Check for Updates', w=300, h=30, 

                backgroundColor=[0.3, 0.5, 0.7], c=check_updates_menu)

    cmds.separator()

    

    cmds.text(label='v{0} - Created by Franz Vega'.format(__version__), 

              font="smallObliqueLabelFont", align="right")



    cmds.showWindow(window)

