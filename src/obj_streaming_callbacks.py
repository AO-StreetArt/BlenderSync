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
import threading

from ..animation_client.obj_streaming import send_object_updates, listen_for_object_updates

# Callbacks which are triggered when boolean properties are flipped
def set_aesel_auto_update(self, context):
    if not context.scene.aesel_updates_live:
        context.scene.aesel_updates_live = True
        if not context.scene.aesel_updates_initiated:
            context.scene.aesel_updates_initiated = True
            # Use the blender timer api to schedule sending automatic updates
            # TO-DO: Does this cause any sort of delay in the viewport vs
            #         running on a background thread?
            bpy.app.timers.register(functools.partial(send_object_updates,
                                                      bpy.context.scene.general_api_wrapper,
                                                      bpy.context.scene.object_api_wrapper,
                                                      bpy.types.Scene.event_client,
                                                      bpy.context.scene.aesel_updates_queue))
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
        recv_thread = threading.Thread(target=listen_for_object_updates,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.context.scene.aesel_updates_queue))
        recv_thread.daemon = True
        recv_thread.start()
    else:
        bpy.context.scene.aesel_listen_live = False
