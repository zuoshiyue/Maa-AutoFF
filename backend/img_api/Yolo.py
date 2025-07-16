import onnxruntime as ort
import cv2
import numpy as np
import time
import io
import os
from cryptography.fernet import Fernet

class YoloDetector:
    """YOLO模型检测器类，支持多模型加载和针对不同目标的检测"""
    
    def __init__(self, character_model='res/bin/character.dll', skill_model='res/bin/skill.dll', talent_model='res/bin/talent.dll'):
        """
        初始化YOLO检测器，加载多个模型
        
        参数:
            character_model: 角色检测模型路径
            skill_model: 技能检测模型路径
            talent_model: 天赋检测模型路径
            use_cuda: 是否使用CUDA加速
        """
        # 设置解密密钥
        self.key = b'Bh3v3pp6NWk-ccty9IqN5I0LuYXPu5IiPVSnWvYgECg='
        self.fernet = Fernet(self.key)
        
        # 设置cpu运行
        self.providers = ['CPUExecutionProvider']
        
        # 加载所有模型
        print("正在加载并解密模型...")
        self.models = {}
        self.model_info = {}
        
        try:
            # 加载角色模型
            self.models['character'] = self._load_encrypted_model(character_model)
            self._init_model_info('character')
            print(f"角色模型加载成功: {character_model}")
            
            # 加载技能模型
            self.models['skill'] = self._load_encrypted_model(skill_model)
            self._init_model_info('skill')
            print(f"技能模型加载成功: {skill_model}")
            
            # 加载天赋模型
            self.models['talent'] = self._load_encrypted_model(talent_model)
            self._init_model_info('talent')
            print(f"天赋模型加载成功: {talent_model}")
            
        except Exception as e:
            print(f"模型加载失败: {e}")
            raise
    
    def _load_encrypted_model(self, model_path):
        """
        加载并解密模型
        
        参数:
            model_path: 加密模型的路径
            
        返回:
            解密后的ONNX模型会话
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型文件不存在: {model_path}")
            
            # 读取加密的模型文件
            with open(model_path, 'rb') as file:
                encrypted_data = file.read()
            
            # 解密模型数据
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # 从内存中加载ONNX模型，而不是保存到磁盘
            session = ort.InferenceSession(decrypted_data, providers=self.providers)
            
            return session
            
        except Exception as e:
            print(f"解密和加载模型 {model_path} 时出错: {e}")
            raise
    
    def _init_model_info(self, model_type):
        """初始化模型信息"""
        session = self.models[model_type]
        
        # 获取模型的类别信息
        name_class_str = session.get_modelmeta().custom_metadata_map.get("names")
        name_class_dict = {}
        if isinstance(name_class_str, str):
            try:
                # 解析类别信息字符串
                items = name_class_str.strip('{}').split(', ')
                for item in items:
                    parts = item.split(':', 1)
                    if len(parts) == 2:
                        k, v = parts
                        name_class_dict[int(k)] = v.strip().strip("'\"")
            except Exception as e:
                print(f"解析{model_type}模型类别信息失败: {e}")
        
        # 获取输入输出信息
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        input_shape = session.get_inputs()[0].shape
        
        # 存储模型信息
        self.model_info[model_type] = {
            'class_dict': name_class_dict,
            'input_name': input_name,
            'output_name': output_name,
            'input_shape': input_shape
        }
    
    def preprocess_image(self, img, input_shape):
        """预处理图像以适应ONNX模型输入"""
        # 调整图像大小以匹配模型输入尺寸
        height, width = input_shape[2], input_shape[3] if len(input_shape) > 3 else input_shape[2]
        img = cv2.resize(img, (width, height))
        
        # 转换为RGB（如果是BGR）
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 归一化图像 [0-255] -> [0-1]
        img = img.astype(np.float32) / 255.0
        
        # 添加批次维度并转换为NCHW格式（如果需要）
        if len(input_shape) == 4 and input_shape[1] == 3:  # NCHW格式
            img = img.transpose(2, 0, 1)  # HWC -> CHW
        
        # 扩展批次维度
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def detect_regions(self, img, model_type, recs):
        """
        使用指定类型的模型检测图像中的特定区域
        
        参数:
            img: CV2格式的图像
            model_type: 模型类型，可选 'character', 'skill', 'talent'
            recs: 自定义检测区域，[[x, y, w, h], [x, y, w, h], [x, y, w, h]]
            
        返回:
            检测结果列表
        """
        if img is None:
            raise ValueError("必须提供图像参数img")
        
        if model_type not in self.models:
            raise ValueError(f"不支持的模型类型: {model_type}，可用类型: {list(self.models.keys())}")
        
        # 获取模型信息
        session = self.models[model_type]
        info = self.model_info[model_type]
        input_name = info['input_name']
        output_name = info['output_name']
        input_shape = info['input_shape']
        name_class_dict = info['class_dict']
        
        results = []

        # 对每个矩形区域进行裁剪和预测
        for i, rect in enumerate(recs):
            x, y, w, h = rect
            
            # 确保坐标在图像范围内
            if y >= img.shape[0] or x >= img.shape[1]:
                print(f"警告: 区域 {i+1} 坐标超出图像范围，跳过")
                continue
                
            # 裁剪图像，确保不超出边界
            y_end = min(y + h, img.shape[0])
            x_end = min(x + w, img.shape[1])
            try:
                cropped = img[y:y_end, x:x_end]
            except Exception as e:
                print(f"裁剪区域 {i+1} 时出错: {e}")
                continue
            
            # 检查裁剪是否成功
            if cropped.size == 0:
                print(f"警告: 区域 {i+1} 裁剪后为空，跳过")
                continue
            
            # 预处理图像
            try:
                input_data = self.preprocess_image(cropped, input_shape)
            except Exception as e:
                print(f"预处理区域 {i+1} 时出错: {e}")
                continue
            
            try:
                # 预热一次
                _ = session.run([output_name], {input_name: input_data})
                
                # 多次测量取平均值，获得更稳定的时间
                num_runs = 3
                total_time = 0
                for _ in range(num_runs):
                    start_time = time.time()
                    outputs = session.run([output_name], {input_name: input_data})
                    total_time += (time.time() - start_time)
                
                inference_time = (total_time / num_runs) * 1000  # 转换为毫秒
                
                # 获取预测结果
                output = outputs[0]
                top1_cls = np.argmax(output)
                top1_conf = float(output[0][top1_cls])
                
                # 将类别索引转换为字符串
                model_class_name = name_class_dict.get(int(top1_cls), f"未知类别_{top1_cls}")
                
                # 打印类别索引和对应的真实类别名称
                # print(f"区域 {i+1}:")
                # print(f"  类别索引: {top1_cls}")
                # print(f"  模型类别名称: {model_class_name}")
                # print(f"  置信度: {top1_conf:.2f}")
                # print(f"  推理耗时: {inference_time:.1f}ms")
                
                # 收集结果，置信度保留两位小数
                results.append({
                    "class_name": model_class_name,
                    "confidence": round(float(top1_conf), 2),
                    "region": [x, y, w, h]
                })
            except Exception as e:
                print(f"处理区域 {i+1} 时出错: {e}")
                continue
        
        return results
    
    # 检测角色
    def detect_characters(self, img: np.ndarray, recs_str):
        if recs_str == 'lianmeng':    # 联盟人物选择
            recs = [[444,270,131,156], [706,270,131,156]]
        
        # 获取原始检测结果
        raw_results = self.detect_regions(img, 'character', recs)
        
        # 格式化结果
        formatted_results = []
        
        # 创建一个字典，用于快速查找每个区域的结果
        region_results = {}
        for result in raw_results:
            region = tuple(result['region'])  # 转换为元组以便作为字典键
            region_results[region] = [result['class_name'], result['confidence']]
        
        # 按照recs的顺序生成结果
        for rect in recs:
            rect_tuple = tuple(rect)
            if rect_tuple in region_results:
                formatted_results.append(region_results[rect_tuple])
            else:
                formatted_results.append(['空', 0])
        
        return formatted_results
    
    # 检测技能
    def detect_skills(self, img: np.ndarray, recs_str):
        if recs_str in ['zongshi', 'zixuan', 'wujin']:    # 宗师技能
            recs = [[350,275,68,68], [600,275,68,68], [855,275,68,68]]
        elif recs_str == 'shangdian':    # 技能商店
            recs = [[284,222,74,74], [602,222,74,74], [919,222,74,74]]
        elif recs_str == 'lianmeng':    # 联盟技能-已缩小
            recs = [[329,270,57,57], [609,270,57,57], [889,270,57,57]]
        
        # 获取原始检测结果
        raw_results = self.detect_regions(img, 'skill', recs)
        
        # 格式化结果
        formatted_results = []
        
        # 创建一个字典，用于快速查找每个区域的结果
        region_results = {}
        for result in raw_results:
            region = tuple(result['region'])  # 转换为元组以便作为字典键
            region_results[region] = [result['class_name'], result['confidence']]
        
        # 按照recs的顺序生成结果
        for rect in recs:
            rect_tuple = tuple(rect)
            if rect_tuple in region_results:
                formatted_results.append(region_results[rect_tuple])
            else:
                formatted_results.append(['空', 0])
        
        return formatted_results
    
    
    # 检测天赋
    def detect_talents(self, img: np.ndarray, recs_str):
        if recs_str in ['zongshi', 'zixuan', 'wujin']:    # 宗师天赋-已缩小
            recs = [[414,259,50,50], [616,259,50,50], [818,259,50,50]]
        elif recs_str == 'lianmeng':    # 联盟天赋-已缩小
            recs = [[408,262,50,50], [616,262,50,50], [824,262,50,50]]
        
        # 获取原始检测结果
        raw_results = self.detect_regions(img, 'talent', recs)
        
        # 格式化结果
        formatted_results = []
        
        # 创建一个字典，用于快速查找每个区域的结果
        region_results = {}
        for result in raw_results:
            region = tuple(result['region'])  # 转换为元组以便作为字典键
            region_results[region] = [result['class_name'], result['confidence']]
        
        # 按照recs的顺序生成结果
        for rect in recs:
            rect_tuple = tuple(rect)
            if rect_tuple in region_results:
                formatted_results.append(region_results[rect_tuple])
            else:
                formatted_results.append(['空', 0])

        # 处理能量掠夺_3和能量_3的替换
        special_talents = ['暴击', '攻速', '爆伤', '护盾', '回能']
        # 提取基础天赋名称（去掉_和等级）进行比较，必须完全匹配
        has_special = any(any(talent[0].split('_')[0] == special for special in special_talents) for talent in formatted_results)
        # 使用一行代码处理所有等级的能量掠夺和能量替换
        formatted_results = [[talent[0].replace('能量掠夺_3', '能量_3').replace('能量掠夺_2', '能量_2').replace('能量掠夺_1', '能量_1') if has_special else talent[0].replace('能量_3', '能量掠夺_3').replace('能量_2', '能量掠夺_2').replace('能量_1', '能量掠夺_1'), talent[1]] for talent in formatted_results]
        
        return formatted_results