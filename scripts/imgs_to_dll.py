import os
import json
import base64
import numpy as np
import cv2
from cryptography.fernet import Fernet

imgs_path = "backend/imgs"
dll_path = "res/bin/imgs.dll"

# 加密密钥
key = "Bh3vgV16NWk-cc91fIqN28d9uY4Vu5Ii72Snv1YgECg="

def generate_encrypted_images():
    # 获取imgs目录下所有的png和jpg文件
    image_files = [f for f in os.listdir(imgs_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # 创建一个字典来存储图像数据
    images_data = {}
    
    for image_file in image_files:
        file_path = os.path.join(imgs_path, image_file)
        try:
            # 读取图像
            with open(file_path, 'rb') as f:
                img_data = f.read()
                
            # 将图像数据转换为base64编码
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # 存储到字典中，使用文件名（不含扩展名）作为键
            image_name = os.path.splitext(image_file)[0]
            images_data[image_name] = img_base64
            
            print(f"处理图像: {image_file}")
        except Exception as e:
            print(f"处理图像 {image_file} 时出错: {str(e)}")
    
    # 将字典转换为JSON字符串
    json_data = json.dumps(images_data)
    
    # 使用Fernet加密JSON数据
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json_data.encode('utf-8'))
    
    # 将加密后的数据保存为DLL文件
    with open(dll_path, "wb") as f:
        f.write(encrypted_data)
    
    print(f"已生成加密的DLL文件: imgs.dll")

if __name__ == "__main__":
    generate_encrypted_images() 