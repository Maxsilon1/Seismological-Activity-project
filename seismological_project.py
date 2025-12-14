import numpy as np
import matplotlib.pyplot as plt

def generate_signal(N):
    t = np.arange(N)
    signal = np.sin(2 * np.pi * t / N) + 0.5 * np.sin(8 * np.pi * t / N)
    return signal

#O(n^2)
def DFT(f):
    N = len(f)
    F = np.zeros(N, dtype = complex)
    for n in range(N):
        for k in range(N):
            exponent = -2j * n * np.pi * k/N
            F[n] += f[k] * np.exp(exponent)

    return F

def FFT(f, inverse):
    N = len(f)

    if N <= 1:
        return f

    even = FFT(f[0::2])
    odd = FFT(f[1::2])

    sign = 1j if inverse else -1j

    F = np.zeros(N, dtype = complex)
    for k in range(N // 2):
        W = np.exp(2 * sign * np.pi * k / N)
        T = W * odd[k]#Домножаем на доп коэф ибо odd впереди на один шаг
        F[k] = even[k] + T
        F[k + N // 2] = even[k] - T#После прохождения половины оно начинает повторяться
    return F

def IFFT(F):
    N = len(F)
    result = FFT(F, True)
    return result / N

def main():
    N = 128 

    a = int(input("Левая граница спектра"))
    b = int(input("Правая граница спектра"))

    half_n = N // 2
    amplitudes = np.abs(F[:half_n]) / 

    # Генерируем входной массив (f_k)
    signal = generate_signal(N)

    result_dft = DFT(signal)
    result_fft = FFT(signal)

    filtered = result_fft

    for k in range(N):
        if not(a <= result_fft <= b or a <= N - result_fft <= b):
            filtered[k] = 0

    #result_numpy = np.fft.fft(signal)

    print("\n--- Результаты (первые 4 значения) ---")

    print("DFT:", np.round(result_dft[:4], 2))
    print("FFT:     ", np.round(result_fft[:4], 2))
    print("NumPy FFT:      ", np.round(result_numpy[:4], 2))

#plt.plot(result_dft, label = 'DFT')
