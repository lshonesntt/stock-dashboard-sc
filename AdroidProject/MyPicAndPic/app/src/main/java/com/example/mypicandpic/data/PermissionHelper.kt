package com.example.mypicandpic.data

import android.Manifest
import android.app.Activity
import android.content.Context
import android.os.Build

object PermissionHelper {

     /**
      * Determines which permission(s) to request based on SDK version.
      */
    val permissions: Array<String>
        get() = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(Manifest.permission.READ_MEDIA_IMAGES)
         } else {
            arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
         }

     /**
      * Requests all needed permissions at once.
      */
    fun requestPermissions(
        context: Context,
        onGranted: () -> Unit,
        onDenied: () -> Unit
     ) {
        val activity = context as? Activity ?: return
        val perms = permissions

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            activity.checkSelfPermission(Manifest.permission.READ_MEDIA_IMAGES) == android.content.pm.PackageManager.PERMISSION_GRANTED) {
            onGranted()
            return
         }
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU &&
            activity.checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE) == android.content.pm.PackageManager.PERMISSION_GRANTED) {
            onGranted()
            return
         }

        activity.requestPermissions(perms, 1001)
     }

     /**
      * Handles the result of permission request.
      */
    fun handlePermissionResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray,
        onGranted: () -> Unit,
        onDenied: () -> Unit
     ) {
        if (requestCode == 1001) {
            if (permissions.size == grantResults.size && grantResults.all { it == android.content.pm.PackageManager.PERMISSION_GRANTED }) {
                onGranted()
             } else {
                onDenied()
             }
         }
     }
}
