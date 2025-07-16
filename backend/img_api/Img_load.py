import json
import base64
import numpy as np
import cv2
from cryptography.fernet import Fernet

class ImageLoader:
    def __init__(self, dll_path="res/bin/imgs.dll", key="Bh3vgV16NWk-cc91fIqN28d9uY4Vu5Ii72Snv1YgECg="):
        """
        初始化图像加载器
        
        参数:
            dll_path: 加密DLL文件的路径
            key: 解密密钥
        """
        self.key = key
        self.dll_path = dll_path
        self.images_data = {}
        self._load_images()
    
    def _load_images(self):
        """加载并解密DLL文件中的图像数据"""
        try:
            # 读取加密的DLL文件
            with open(self.dll_path, "rb") as f:
                encrypted_data = f.read()
            
            # 解密数据
            fernet = Fernet(self.key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # 解析JSON数据
            self.images_data = json.loads(decrypted_data.decode('utf-8'))
            
            print(f"成功加载了 {len(self.images_data)} 个图像")
        except Exception as e:
            print(f"加载图像时出错: {str(e)}")
    
    def __getattr__(self, name):
        """
        通过属性访问图像，例如: loader.技能
        
        参数:
            name: 图像名称
        
        返回:
            numpy.ndarray: 图像数据
        """
        if name in self.images_data:
            # 从base64解码图像数据
            img_data = base64.b64decode(self.images_data[name])
            
            # 将二进制数据转换为numpy数组
            nparr = np.frombuffer(img_data, np.uint8)
            
            # 使用OpenCV解码图像
            img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            
            return img
        else:
            raise AttributeError(f"找不到名为 '{name}' 的图像")
    
    def get_image_names(self):
        """获取所有可用的图像名称列表"""
        return list(self.images_data.keys())


# # 使用示例
# if __name__ == "__main__":
#     # 创建图像加载器实例
#     loader = ImageLoader()
    
#     # 获取所有可用的图像名称
#     image_names = loader.get_image_names()
#     print("可用的图像:", image_names)
    
#     # 尝试加载一个图像（如果存在）
#     if image_names:
#         # 获取第一个图像的名称
#         first_image_name = image_names[0]
        
#         # 通过属性访问获取图像数据
#         try:
#             img_data = getattr(loader, first_image_name)
#             print(f"图像 '{first_image_name}' 的形状: {img_data.shape}")
            
#             # 显示图像
#             cv2.imshow(first_image_name, img_data)
#             cv2.waitKey(0)
#             cv2.destroyAllWindows()
#         except Exception as e:
#             print(f"加载图像时出错: {str(e)}") 