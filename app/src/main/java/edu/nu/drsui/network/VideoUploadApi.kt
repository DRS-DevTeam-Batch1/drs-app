package edu.nu.drsui.network

import okhttp3.MultipartBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface VideoUploadApi {
    @Multipart
    @POST("upload_video/") // Your backend endpoint
    suspend fun uploadVideo(
        @Part video: MultipartBody.Part
    ): Response<ResponseBody>
}