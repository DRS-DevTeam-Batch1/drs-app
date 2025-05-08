package edu.nu.drsui.network

import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface VideoUploadApi {
    @Multipart
    @POST("api/analyze-video") // Match the FastAPI endpoint path
    suspend fun uploadVideo(
        @Part video: MultipartBody.Part,
        @Part("ball_number") ballNumber: RequestBody,
        @Part("over_number") overNumber: RequestBody,
        @Part("capture_angle") captureAngle: RequestBody
    ): Response<ResponseBody>
}
