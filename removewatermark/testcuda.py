import cv2

def test_cuda():
    # Check if OpenCV is built with CUDA support
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        print("OpenCV is built with CUDA support.")
        
        # Initialize a CUDA-enabled GPU matrix
        gpu_mat = cv2.cuda_GpuMat()
        
        # Perform a simple operation on the GPU matrix
        gpu_mat.upload(cv2.imread("image.jpg"))
        gpu_mat = cv2.cuda.cvtColor(gpu_mat, cv2.COLOR_BGR2GRAY)
        
        # Download the result from GPU to CPU
        result = gpu_mat.download()
        
        print("CUDA operations completed successfully.")
    else:
        print("OpenCV is not built with CUDA support.")

# Run the CUDA test
test_cuda()