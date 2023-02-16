import cv2
import numpy as np
# Step 5: Smoothing Transmission Map using Guided Filter
# src: https://github.com/ba-san/Python-image-enhancement-with-bright-dark-prior/blob/master/src/guidedfilter.py
from image_processing.guidedfilter import guided_filter

# Night time photo illumination improvement scripts, using cv2
# https://learnopencv.com/improving-illumination-in-night-time-images/#sec2.1

# Step 1: Obtaining the Bright and Dark channel Prior
def get_illumination_channel(I, w):
    M, N, _ = I.shape
    # padding for channels
    padded = np.pad(
        I, ((int(w / 2), int(w / 2)), (int(w / 2), int(w / 2)), (0, 0)), "edge"
    )
    darkch = np.zeros((M, N))
    brightch = np.zeros((M, N))

    for i, j in np.ndindex(darkch.shape):
        darkch[i, j] = np.min(padded[i : i + w, j : j + w, :])  # dark channel
        brightch[i, j] = np.max(padded[i : i + w, j : j + w, :])  # bright channel

    return darkch, brightch


# Step 2: Computing Global Atmosphere Lighting
def get_atmosphere(I, brightch, p=0.1):
    M, N = brightch.shape
    flatI = I.reshape(M * N, 3)  # reshaping image array
    flatbright = brightch.ravel()  # flattening image array

    searchidx = (-flatbright).argsort()[: int(M * N * p)]  # sorting and slicing
    A = np.mean(flatI.take(searchidx, axis=0), dtype=np.float64, axis=0)
    return A


# Step 3: Finding the Initial Transmission Map
def get_initial_transmission(A, brightch):
    A_c = np.max(A)
    init_t = (brightch - A_c) / (1.0 - A_c)  # finding initial transmission map
    return (init_t - np.min(init_t)) / (
        np.max(init_t) - np.min(init_t)
    )  # normalized initial transmission map


# Step 4: Using Dark Channel to Estimate Corrected Transmission Map
def get_corrected_transmission(I, A, darkch, brightch, init_t, alpha, omega, w):
    im = np.empty(I.shape, I.dtype)
    for ind in range(0, 3):
        im[:, :, ind] = (
            I[:, :, ind] / A[ind]
        )  # divide pixel values by atmospheric light
    dark_c, _ = get_illumination_channel(im, w)  # dark channel transmission map
    dark_t = 1 - omega * dark_c  # corrected dark transmission map
    corrected_t = (
        init_t  # initializing corrected transmission map with initial transmission map
    )
    diffch = brightch - darkch  # difference between transmission maps

    for i in range(diffch.shape[0]):
        for j in range(diffch.shape[1]):
            if diffch[i, j] < alpha:
                corrected_t[i, j] = dark_t[i, j] * init_t[i, j]

    return np.abs(corrected_t)




# Step 6: Calculating the Resultant Image
def get_final_image(I, A, refined_t, tmin):
    refined_t_broadcasted = np.broadcast_to(
        refined_t[:, :, None], (refined_t.shape[0], refined_t.shape[1], 3)
    )  # duplicating the channel of 2D refined map to 3 channels
    J = (I - A) / (
        np.where(refined_t_broadcasted < tmin, tmin, refined_t_broadcasted)
    ) + A  # finding result

    return (J - np.min(J)) / (np.max(J) - np.min(J))  # normalized image


# Further Improvements
# Reduce spotlight
def reduce_init_t(init_t):
    init_t = (init_t * 255).astype(np.uint8)
    xp = [0, 32, 255]
    fp = [0, 32, 48]
    x = np.arange(256)  # creating array [0,...,255]
    table = np.interp(x, xp, fp).astype(
        "uint8"
    )  # interpreting fp according to xp in range of x
    init_t = cv2.LUT(init_t, table)  # lookup table
    init_t = init_t.astype(np.float64) / 255  # normalizing the transmission map
    return init_t


# Combine all functions
def dehaze(
    I,
    tmin=0.1,  # minimum value for t to make J image
    w=15,  # window size, which determine the corseness of prior images
    alpha=0.4,  # threshold for transmission correction
    omega=0.75,  # this is for dark channel prior
    p=0.1,  # percentage to consider for atmosphere
    eps=1e-3,  # for J image
    reduce=False,
):

    I = np.asarray(I, dtype=np.float64)  # Convert the input to a float array.
    I = I[:, :, :3] / 255
    m, n, _ = I.shape
    Idark, Ibright = get_illumination_channel(I, w)
    A = get_atmosphere(I, Ibright, p)

    init_t = get_initial_transmission(A, Ibright)
    if reduce:
        init_t = reduce_init_t(init_t)
    corrected_t = get_corrected_transmission(
        I, A, Idark, Ibright, init_t, alpha, omega, w
    )

    normI = (I - I.min()) / (I.max() - I.min())
    refined_t = guided_filter(normI, corrected_t, w, eps)  # applying guided filter
    J_refined = get_final_image(I, A, refined_t, tmin)

    enhanced = (J_refined * 255).astype(np.uint8)
    f_enhanced = cv2.detailEnhance(enhanced, sigma_s=10, sigma_r=0.15)
    f_enhanced = cv2.edgePreservingFilter(f_enhanced, flags=1, sigma_s=64, sigma_r=0.2)
    return f_enhanced


def average_pixel_value(im):
    img = cv2.imread(im)
    # convert it to RGB channel
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return np.average(img)


if __name__ == "__main__":
    in_ = input("Relative path to image: ")
    im = cv2.imread(in_)
    orig = im.copy()

    I = np.asarray(im, dtype=np.float64)  # Convert the input to an array.
    I = I[:, :, :3] / 255

    f_enhanced2 = dehaze(I, reduce=True)

    cv2.imshow("F_enhanced2", f_enhanced2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
