from PIL import Image, ImageOps
import numpy as np
import json

def calcular_histograma(imagem):
    histograma = imagem.histogram()
    histograma_rgb = {
        "R": histograma[0:256],
        "G": histograma[256:512],
        "B": histograma[512:768]
    }
    return histograma_rgb

def gerar_histograma_json(caminho_imagem):
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    
    # Converte a imagem para RGB
    if (imagem.mode != 'RGB'):
        imagem = imagem.convert('RGB')
    
    # Calcula o histograma
    histograma_rgb = calcular_histograma(imagem)
    
    # Converte para JSON sem indentação
    histograma_json = json.dumps(histograma_rgb)
    
    return histograma_json

def save_compressed_data_to_json(compressed_data, output_path):
    with open(output_path, 'w') as json_file:
        json.dump(compressed_data, json_file) 

def halftone(image_path, output_path, dot_size=10):
    # Abra a imagem e converta para escala de cinza
    img = Image.open(image_path).convert('L')
    
    # Inverte a imagem para ter pontos pretos em fundo branco
    img = ImageOps.invert(img)
    
    # Converte a imagem em um array numpy
    img_array = np.array(img)
    
    # Cria uma nova imagem para aplicar o halftone
    halftone_img = Image.new('L', img.size, 255)
    pixels = halftone_img.load()
    
    # Aplica o algoritmo de halftone
    for y in range(0, img_array.shape[0], dot_size):
        for x in range(0, img_array.shape[1], dot_size):
            # Verifica os limites da imagem para não exceder
            region = img_array[y:y + dot_size, x:x + dot_size]
            avg_intensity = np.mean(region)
            
            # Calcula o raio do círculo para simular o halftone
            radius = int((avg_intensity / 255) * (dot_size // 2))
            for i in range(dot_size):
                for j in range(dot_size):
                    if (i - dot_size // 2) ** 2 + (j - dot_size // 2) ** 2 <= radius ** 2:
                        # Certifica-se de que o ponto está dentro dos limites da imagem
                        if x + i < img_array.shape[1] and y + j < img_array.shape[0]:
                            pixels[x + i, y + j] = 0  # Desenha o ponto preto
    
    # Salva a nova imagem
    halftone_img.save(output_path)

def compress_image_rle(image_path):
    # Carregar a imagem e converter para escala de cinza
    image = Image.open(image_path).convert('L')
    pixels = list(image.getdata())
    
    # Aplicar RLE
    compressed_data = []
    current_pixel = pixels[0]
    count = 0

    for pixel in pixels:
        if pixel == current_pixel:
            count += 1
        else:
            compressed_data.append([current_pixel, count])
            current_pixel = pixel
            count = 1
    
    # Adicionar o último grupo
    compressed_data.append([current_pixel, count])

    return compressed_data

def decompress_image_rle(json_path, output_image_path, image_size):
    # Ler o arquivo JSON
    with open(json_path, 'r') as json_file:
        compressed_data = json.load(json_file)

    # Descomprimir os dados
    decompressed_pixels = []
    for pixel_value, count in compressed_data:
        decompressed_pixels.extend([pixel_value] * count)

    # Verificar se o número de pixels é igual ao esperado
    expected_pixel_count = image_size[0] * image_size[1]
    if len(decompressed_pixels) != expected_pixel_count:
        raise ValueError(f"Erro: Número de pixels descomprimidos ({len(decompressed_pixels)}) "
                         f"não corresponde ao tamanho da imagem ({expected_pixel_count}).")

    # Criar a imagem a partir dos pixels descomprimidos
    image = Image.new('L', image_size)
    image.putdata(decompressed_pixels)
    image.save(output_image_path)

def loadSizeImage(imagem):
    # Carrega a imagem
    imagem = Image.open(caminho_da_imagem)
    # Obtém a largura e a altura da imagem
    return imagem.size
    



#Variaveis
caminho_da_imagem = 'Chris.jpeg'
output_path = 'histograma.json'
output_path_comprimed = 'imagem_comprimida.json'
output_path_halftone = 'imagem_halftone.jpg'
output_path_uncompressed = 'imagem_descomprimida.png'


#Funcoes
compressed_data = compress_image_rle(caminho_da_imagem)
histograma_json = gerar_histograma_json(caminho_da_imagem)
save_compressed_data_to_json(histograma_json, output_path)
save_compressed_data_to_json(compressed_data, output_path_comprimed)
halftone(caminho_da_imagem, output_path_halftone, dot_size=10)
decompress_image_rle(output_path_comprimed, output_path_uncompressed, loadSizeImage(caminho_da_imagem))
