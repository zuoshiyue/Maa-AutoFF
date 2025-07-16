from rapidocr import RapidOCR, OCRVersion
import numpy as np
import re
from typing import Union, List, Tuple, Any, Optional

class Ocr:
    def __init__(self):
        self.engine = RapidOCR(
            params={
        "Rec.ocr_version": OCRVersion.PPOCRV5
    }
        )

    # 仅文本识别
    def only_text(self, img: np.ndarray, regions: Union[List[int], List[List[int]]]) -> List[Optional[str]]:
        """
        仅进行文本识别，不进行文本检测和方向分类
        
        Args:
            img: 输入图像，numpy数组格式
            regions: 检测坐标，可以是单个[x,y,w,h]或多个[[x,y,w,h], ...]
            
        Returns:
            List[Optional[str]]: 识别结果列表，如果某区域无识别结果则为None
        """
        # 判断regions是否为单个坐标
        if isinstance(regions, list) and len(regions) > 0:
            if isinstance(regions[0], int):
                # 单个坐标情况，转换为列表格式
                regions = [regions]
        
        results = []
        
        # 处理每个区域
        for region in regions:
            x, y, w, h = region
            
            # 确保坐标在图像范围内
            x = max(0, min(x, img.shape[1] - 1))
            y = max(0, min(y, img.shape[0] - 1))
            w = min(w, img.shape[1] - x)
            h = min(h, img.shape[0] - y)
            
            # 裁剪区域
            crop_img = img[y:y+h, x:x+w]
            
            # 如果裁剪区域为空，添加None结果
            if crop_img.size == 0:
                results.append(None)
                continue
            
            # 进行OCR识别，仅使用文本识别，不使用检测和分类
            ocr_result = self.engine(crop_img, use_det=False, use_cls=False, use_rec=True)
            
            # 解析结果
            if ocr_result and len(ocr_result[0]) > 0:
                # ocr_result格式为: ([['文本', 置信度]], [耗时])
                # 取第一个结果的文本并去除特殊符号
                text = ocr_result[0][0][0]
                # 使用正则表达式去除特殊符号，只保留中文、英文和数字
                text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text)
                # 结果修正
                text = text.replace('銀', '')
                results.append(text)
            else:
                results.append(None)
        
        return results
    
    # 检测+分类+识别 ---- bug，只写了识别第一个区域
    def detect(self, img: np.ndarray, regions: Union[List[int], List[List[int]]], use_det: bool = True, use_cls: bool = False, use_rec: bool = True) -> List[Optional[str]]:
        # 判断regions是否为单个坐标
        if isinstance(regions, list) and len(regions) > 0:
            if isinstance(regions[0], int):
                # 单个坐标情况，转换为列表格式
                regions = [regions]
        
        result = {}
        
        # 处理每个区域
        for region in regions:
            x, y, w, h = region
            
            # 确保坐标在图像范围内
            x = max(0, min(x, img.shape[1] - 1))
            y = max(0, min(y, img.shape[0] - 1))
            w = min(w, img.shape[1] - x)
            h = min(h, img.shape[0] - y)
            
            # 裁剪区域
            crop_img = img[y:y+h, x:x+w]
            
            # 如果裁剪区域为空，添加None结果
            if crop_img.size == 0:
                continue
            
            # 进行OCR识别，仅使用文本识别，不使用检测和分类
            ocr_result = self.engine(crop_img, use_det=use_det, use_cls=use_cls, use_rec=use_rec)
            for i in range(len(ocr_result.txts)):
                r_x = int(ocr_result.boxes[i][0][0]+x)
                r_y = int(ocr_result.boxes[i][0][1]+y)
                r_w = int(ocr_result.boxes[i][1][0]-ocr_result.boxes[i][0][0])
                r_h = int(ocr_result.boxes[i][2][1]-ocr_result.boxes[i][0][1])
                result[ocr_result.txts[i]] = [r_x, r_y, r_w, r_h]
            return result

            
        