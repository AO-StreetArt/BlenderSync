'''
Copyright (C) 2018 Alex Barry
aostreetart9@gmail.com

Created by Alex Barry

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import socket
import threading

# Listen for updates from Aesel
def listen_for_object_updates():
    addon_prefs = bpy.context.preferences.addons["BlenderSync"].preferences
    server_address = (addon_prefs.udp_host, addon_prefs.udp_port)
    print('Opening UDP Port: %s :: %s' % server_address)
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # AES-256-cbc Decryption
    cipher_backend = default_backend()
    cipher = Cipher(algorithms.AES(addon_prefs.aesel_udp_decryption_key), modes.CBC(addon_prefs.aesel_udp_decryption_iv), backend=cipher_backend)

    # Bind the socket to the port
    sock.bind(server_address)
    while(bpy.context.scene.aesel_listen_live):
        # Recieve a message from Aesel
        data, address = sock.recvfrom(8192)
        print(data)
        data_str = None
        if data:
            # Decode the recieved data, and decrypt if necessary
            if addon_prefs.udp_encryption_active:
                decryptor = cipher.decryptor()
                data_str = decryptor.update(bytes(msg, 'UTF-8')) + decryptor.finalize()
            else:
                data_str = data.decode("utf-8")
            print("Recieved data %s" % data_str)

            # Parse the data and drop it onto a queue for processing
            data_dict = json.loads(data_str)
            data_dict["type"] = "live_update"
            bpy.context.scene.aesel_updates_queue.put(data_dict)
    print("Not listening on UDP port anymore")

def send_object_updates():
    if bpy.context.scene.aesel_updates_live:
        addon_prefs = bpy.context.preferences.addons["BlenderSync"].preferences
        for elt in bpy.context.scene.aesel_live_objects:
            obj = bpy.data.objects[elt[1]]
            print("Sending UDP update for object %s" % elt[1])
            aesel_obj = AeselObject()
            aesel_obj.key = elt[0]
            aesel_obj.name = elt[1]
            aesel_obj.scene = scene_mgmt.get_selected_scene(bpy.context)
            aesel_obj.transform = [obj.matrix_world[0][0], obj.matrix_world[0][1],
                                   obj.matrix_world[0][2], obj.matrix_world[0][3],
                                   obj.matrix_world[1][0], obj.matrix_world[1][1],
                                   obj.matrix_world[1][2], obj.matrix_world[1][3],
                                   obj.matrix_world[2][0], obj.matrix_world[2][1],
                                   obj.matrix_world[2][2], obj.matrix_world[2][3],
                                   obj.matrix_world[3][0], obj.matrix_world[3][1],
                                   obj.matrix_world[3][2], obj.matrix_world[3][3]]
            # Send the actual message
            bpy.types.Scene.event_client.send_object_update(aesel_obj)
    # Return 1 / (updates per second) for the blender timer api
    return 1.0 / addon_prefs.update_rate

# Callbacks which are triggered when boolean properties are flipped
def set_aesel_auto_update(self, context):
    if not context.scene.aesel_updates_live:
        context.scene.aesel_updates_live = True
        if not context.scene.aesel_updates_initiated:
            context.scene.aesel_updates_initiated = True
            # Use the blender timer api to schedule sending automatic updates
            # TO-DO: Does this cause any sort of delay in the viewport vs
            #         running on a background thread?
            bpy.app.timers.register(send_object_updates)
    else:
        context.scene.aesel_updates_live = False

def set_aesel_listen(self, context):
    if not bpy.context.scene.aesel_listen_live:
        bpy.context.scene.aesel_listen_live = True

        # Start a background thread to listen on the UDP socket and put
        # the messages onto a queue, where they can be picked up by a
        # timer on the main thread to update the actual blender data.
        # this is the suggested design pattern in the blender docs:
        # https://docs.blender.org/api/blender2.8/bpy.app.timers.html#use-a-timer-to-react-to-events-in-another-thread
        recv_thread = threading.Thread(target=listen_for_object_updates, args=())
        recv_thread.daemon = True
        recv_thread.start()
    else:
        bpy.context.scene.aesel_listen_live = False
