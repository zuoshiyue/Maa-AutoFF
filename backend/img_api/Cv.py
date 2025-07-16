import cv2
import numpy as np
import os
from dataclasses import dataclass
from typing import Optional, List, Tuple, Union, Dict, Any

@dataclass
class MatchResult:
    """特征匹配结果类"""
    rect: Tuple[int, int, int, int]  # (x, y, w, h)
    score: float  # 匹配分数
    count: int  # 匹配点数量
    name: str = ""  # 匹配的图像名称

class MatchResultContainer:
    """匹配结果容器类，允许通过图片名称访问匹配结果"""
    def __init__(self):
        self._results = {}
        
    def add_result(self, name: str, result: Optional[MatchResult]):
        """添加匹配结果"""
        self._results[name] = result
        
    def __getattr__(self, name: str) -> Optional[MatchResult]:
        """通过属性访问匹配结果"""
        return self._results.get(name)
        
    def __str__(self) -> str:
        """字符串表示"""
        result = []
        for name, match in self._results.items():
            if match:
                result.append(f"{name}: {match}")
            else:
                result.append(f"{name}: None")
        return "\n".join(result)
        
    def __repr__(self) -> str:
        return self.__str__()

# 单图像匹配
def SingleMatch(img: np.ndarray, template_info: List[Any]) -> Optional[MatchResult]:
    """单图像匹配函数
    
    参数:
        img: 输入图像
        template_info: 单个模板信息，格式为：[图像名称, np.ndarray, 匹配参数]
                       
                       匹配参数是一个字典: {
                           'method': "Feature"或"Template",
                           ... 其他参数对应FeatureMatch或TemplateMatch的参数
                       }
    
    返回:
        匹配成功时返回MatchResult对象（包含name字段），失败时返回None
    """
    # 校验输入格式
    if len(template_info) != 3:
        return None
        
    name, template_img, params = template_info
    
    # 检查参数有效性
    if not isinstance(params, dict) or 'method' not in params:
        return None
        
    if template_img is None:
        return None
        
    # 复制参数字典，不修改原始字典
    match_params = params.copy()
    method = match_params.pop('method')
    
    # 根据匹配方法调用相应函数
    if method == "Feature":
        result = FeatureMatch(img, template_img, **match_params)
    elif method == "Template":
        result = TemplateMatch(img, template_img, **match_params)
    else:
        result = None
    
    # 如果找到匹配，添加名称并返回结果
    if result is not None:
        result.name = name
    
    return result


# 多图像匹配
def MultiMatch(img: np.ndarray, templates: List[List[Any]], return_all: bool = True) -> Union[MatchResultContainer, Optional[MatchResult]]:
    """一次性识别多张图像
    
    参数:
        img: 输入图像
        templates: 模板信息，格式为列表: [[图像名称, np.ndarray, 匹配参数], ...]
                   
                   匹配参数是一个字典: {
                       'method': "Feature"或"Template",
                       ... 其他参数对应FeatureMatch或TemplateMatch的参数
                   }
        return_all: 是否返回所有结果，默认为True
                    - True: 返回MatchResultContainer对象，包含所有模板的匹配结果
                    - False: 一旦有一个模板匹配成功，立即返回该MatchResult对象，
                             如果所有模板都未匹配成功，则返回None
    
    返回:
        如果return_all为True，返回MatchResultContainer对象，可通过.图像名称访问结果
        如果return_all为False，返回第一个匹配成功的MatchResult对象（包含name字段）或None
    """
    result_container = MatchResultContainer()
    
    # 处理每个模板
    for template_info in templates:
        if len(template_info) != 3:
            continue
            
        name, template_img, params = template_info
        
        if not isinstance(params, dict) or 'method' not in params:
            result_container.add_result(name, None)
            continue
            
        if template_img is None:
            result_container.add_result(name, None)
            continue
            
        # 复制参数字典，不修改原始字典
        match_params = params.copy()
        method = match_params.pop('method')
        
        # 根据匹配方法调用相应函数
        if method == "Feature":
            result = FeatureMatch(img, template_img, **match_params)
        elif method == "Template":
            result = TemplateMatch(img, template_img, **match_params)
        else:
            result = None
        
        # 如果不需要返回所有结果且找到了匹配
        if not return_all and result is not None:
            # 为结果添加名称
            result.name = name
            return result
            
        result_container.add_result(name, result)
    
    # 如果需要返回所有结果，返回容器
    if return_all:
        return result_container
    
    # 如果不需要返回所有结果，但没有找到匹配，返回None
    return None


# 特征匹配
def FeatureMatch(img: np.ndarray, template: np.ndarray,
                region: Optional[List[int]] = None, count: int = 8,
                order_by: str = "Horizontal", index: int = 0,
                green_mask: bool = False, detector: str = "SIFT",
                ratio: float = 0.7) -> Optional[MatchResult]:
    """特征匹配函数
    
    参数:
        img: 输入图像
        template: 模板图像
        region: 感兴趣区域 [x, y, w, h]
        count: 匹配所需的最小特征点数量
        order_by: 结果排序方式 "Horizontal"|"Vertical"|"Score"|"Area"|"Random"
        index: 返回结果的索引，-1表示返回所有结果
        green_mask: 是否使用绿色掩码排除模板中的绿色部分
        detector: 特征检测器类型 "SIFT"|"ORB"|"KAZE"|"AKAZE"|"BRISK"
        ratio: 特征匹配距离比率阈值
        
    返回:
        MatchResult对象或None
    """
    # 1. 提取ROI区域
    roi_x, roi_y, roi_w, roi_h = (0, 0, img.shape[1], img.shape[0])
    if region is not None:
        roi_x, roi_y, roi_w, roi_h = region
        
        # 确保ROI在图像范围内
        roi_x = max(0, min(roi_x, img.shape[1] - 1))
        roi_y = max(0, min(roi_y, img.shape[0] - 1))
        roi_w = min(roi_w, img.shape[1] - roi_x)
        roi_h = min(roi_h, img.shape[0] - roi_y)
        
    roi_image = img[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
    
    # 2. 检查图像有效性
    if roi_image.size == 0 or roi_w <= 0 or roi_h <= 0:
        return None
    
    # 3. 配置特征检测器
    detector_map = {
        "SIFT": cv2.SIFT_create(),
        "KAZE": cv2.KAZE_create(),
        "AKAZE": cv2.AKAZE_create(),
        "BRISK": cv2.BRISK_create(),
        "ORB": cv2.ORB_create()
    }
    
    if detector not in detector_map:
        detector = "SIFT"  # 默认使用SIFT
    
    feature_detector = detector_map[detector]
    
    # 4. 处理绿色掩码
    mask = None
    if green_mask:
        mask = np.ones(roi_image.shape[:2], dtype=np.uint8) * 255
        if len(roi_image.shape) == 3:
            green_pixels = np.all(roi_image == [0, 255, 0], axis=2)
            mask[green_pixels] = 0
    
    # 检测ROI的特征点和描述符
    kp1, des1 = feature_detector.detectAndCompute(roi_image, mask)
    
    if des1 is None or len(kp1) < 2:
        return None
    
    # 检测模板的特征点和描述符
    kp2, des2 = feature_detector.detectAndCompute(template, None)
    
    if des2 is None or len(kp2) < 2:
        return None
    
    # 特征匹配
    try:
        if detector in ["SIFT", "KAZE"]:
            # SIFT和KAZE使用NORM_L2
            bf = cv2.BFMatcher_create(cv2.NORM_L2)
        else:
            # ORB, AKAZE和BRISK使用NORM_HAMMING
            bf = cv2.BFMatcher_create(cv2.NORM_HAMMING)
        
        matches = bf.knnMatch(des1, des2, k=2)
        
        # 应用比率测试
        good_matches = []
        for m, n in matches:
            if m.distance < ratio * n.distance:
                good_matches.append(m)
    except Exception as e:
        # 特征匹配失败时，记录错误并返回None
        print(f"特征匹配失败: {e}")
        return None
    
    if len(good_matches) < count:
        return None
    
    # 获取匹配点坐标
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    
    # 计算单应性矩阵
    H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
    
    if H is None:
        return None
    
    # 获取模板尺寸
    h, w = template.shape[:2]
    
    # 计算模板在图像中的位置
    pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, H)
    
    # 计算边界框
    x_coords = dst[:, 0, 0]
    y_coords = dst[:, 0, 1]
    x1, y1 = int(min(x_coords)), int(min(y_coords))
    x2, y2 = int(max(x_coords)), int(max(y_coords))
    
    # 确保坐标在ROI范围内
    x1 = max(0, min(x1, roi_image.shape[1] - 1))
    y1 = max(0, min(y1, roi_image.shape[0] - 1))
    x2 = max(x1, min(x2, roi_image.shape[1] - 1))
    y2 = max(y1, min(y2, roi_image.shape[0] - 1))
    
    # 计算匹配分数
    score = len(good_matches)
    
    # 将坐标转换回原图坐标系
    x1 += roi_x
    y1 += roi_y
    x2 += roi_x
    y2 += roi_y
    
    # 确保最终坐标在图像范围内
    x1 = max(0, min(x1, img.shape[1] - 1))
    y1 = max(0, min(y1, img.shape[0] - 1))
    x2 = max(x1, min(x2, img.shape[1] - 1))
    y2 = max(y1, min(y2, img.shape[0] - 1))
    
    # 创建结果
    results = [MatchResult(
        rect=(x1, y1, x2 - x1, y2 - y1),
        score=round(score / len(matches) if matches else 0, 2),
        count=score
    )]
    
    # 根据order_by排序
    if order_by == "Score":
        results.sort(key=lambda x: x.score, reverse=True)
    elif order_by == "Area":
        results.sort(key=lambda x: x.rect[2] * x.rect[3], reverse=True)
    elif order_by == "Vertical":
        results.sort(key=lambda x: x.rect[1])
    elif order_by == "Random":
        np.random.shuffle(results)
    else:  # Horizontal
        results.sort(key=lambda x: x.rect[0])
    
    # 处理索引
    if index == -1:
        return results
    
    if index < 0:
        index = len(results) + index
    
    if 0 <= index < len(results):
        return results[index]
    else:
        return None


# 模板匹配
def TemplateMatch(img: np.ndarray, template: np.ndarray,
                region: Optional[List[int]] = None, match_threshold: float = 0.7, 
                method: int = 5, color_sensitive: bool = False, 
                order_by: str = "Horizontal", index: int = 0, 
                green_mask: bool = False) -> Optional[Union[MatchResult, List[MatchResult]]]:
    """在图像中查找模板匹配的位置
    
    参数:
        img: 输入图像
        template: 模板图像
        region: 感兴趣区域 [x, y, w, h]
        match_threshold: 匹配阈值
        method: 匹配方法
        color_sensitive: 是否进行颜色敏感匹配
        order_by: 结果排序方式 "Horizontal"|"Vertical"|"Score"|"Random"
        index: 返回结果的索引，-1表示返回所有结果
        green_mask: 是否使用绿色掩码排除模板中的绿色部分
        
    返回:
        MatchResult对象或None，如果index=-1则返回MatchResult列表
    """
    # 1. 提取ROI区域
    roi_x, roi_y, roi_w, roi_h = (0, 0, img.shape[1], img.shape[0])
    if region is not None:
        roi_x, roi_y, roi_w, roi_h = region
        
        # 确保ROI在图像范围内
        roi_x = max(0, min(roi_x, img.shape[1] - 1))
        roi_y = max(0, min(roi_y, img.shape[0] - 1))
        roi_w = min(roi_w, img.shape[1] - roi_x)
        roi_h = min(roi_h, img.shape[0] - roi_y)
    
    # 裁剪ROI区域
    roi = img[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    
    # 2. 处理绿色掩码
    mask = None
    if template.shape[2] == 4:
        alpha = template[:, :, 3]
        _, mask = cv2.threshold(alpha, 127, 1, cv2.THRESH_BINARY)
    elif green_mask:
        mask = np.ones(template.shape[:2], dtype=np.uint8) * 255
        if len(template.shape) == 3:
            green_pixels = np.all(template == [0, 255, 0], axis=2)
            mask[green_pixels] = 0
    
    # 3. 对图像和模板进行灰度化
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template

    # 4. 执行模板匹配
    res = cv2.matchTemplate(roi_gray, template_gray, method, mask=mask) if mask is not None else cv2.matchTemplate(roi_gray, template_gray, method)

    # 5. 查找匹配位置 - 排除inf值
    valid_mask = ~np.isinf(res)
    res_valid = np.where(valid_mask, res, -np.inf)  # 将inf值替换为-inf，确保不会被选中
    loc = np.where(res_valid >= match_threshold)
    points = list(zip(*loc[::-1]))
    
    # 6. 处理匹配结果
    matches = []
    for pt in points:
        # 原始ROI中的相对坐标
        rx, ry = pt[0], pt[1]
        
        # 再次检查，确保分数不是inf
        if np.isinf(res[ry, rx]):
            continue
        
        # 如果需要颜色敏感匹配
        if color_sensitive:
            # 获取匹配区域的图像 - 使用ROI内的相对坐标
            if (ry + template.shape[0] <= roi.shape[0] and 
                rx + template.shape[1] <= roi.shape[1]):
                sub_roi = roi[ry:ry + template.shape[0], rx:rx + template.shape[1]]
                if sub_roi.shape[:2] != template.shape[:2]:
                    continue
                    
                # 如果模板有Alpha通道，则转换为BGR以进行颜色比较
                template_to_compare = template
                if len(template.shape) == 3 and template.shape[2] == 4:
                    template_to_compare = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
                    
                # 确保转换后形状仍然匹配
                if sub_roi.shape != template_to_compare.shape:
                    continue

                # 计算颜色差异
                color_diff = np.mean(np.abs(sub_roi.astype(np.float32) - template_to_compare.astype(np.float32)))
                if color_diff > 30:  # 颜色差异阈值，可以根据需要调整
                    continue
            else:
                continue
        
        # 转换为原图坐标系
        x = rx + roi_x
        y = ry + roi_y
        
        # 计算匹配分数
        score = round(float(res[ry, rx]), 2)
        
        # 创建MatchResult对象
        match_result = MatchResult(
            rect=(x, y, template.shape[1], template.shape[0]),
            score=score,
            count=1
        )
        
        # 避免重复结果
        if not any(np.allclose((r.rect[0], r.rect[1]), (match_result.rect[0], match_result.rect[1])) for r in matches):
            matches.append(match_result)

    # 7. 根据order_by排序
    if order_by == "Score":
        matches.sort(key=lambda x: x.score, reverse=True)
    elif order_by == "Vertical":
        matches.sort(key=lambda x: x.rect[1])
    elif order_by == "Random":
        np.random.shuffle(matches)
    else:  # Horizontal
        matches.sort(key=lambda x: x.rect[0])
    
    # 8. 处理返回结果
    if not matches:
        return None
    
    # 返回所有结果
    if index == -1:
        # 更新count为总匹配数
        for i in range(len(matches)):
            matches[i] = MatchResult(
                rect=matches[i].rect,
                score=matches[i].score,
                count=len(matches)
            )
        return matches
    
    # 处理索引
    if index < 0:
        index = len(matches) + index
    
    if 0 <= index < len(matches):
        # 更新count为总匹配数
        return MatchResult(
            rect=matches[index].rect,
            score=matches[index].score,
            count=len(matches)
        )
    else:
        return None



# 比较颜色-单/多点
def CompareColor(img: np.ndarray, pois: Union[List[int], List[List[int]]], color: str) -> bool:
    """比较图像中一个或多个点的颜色是否与指定颜色（及偏色）匹配

    参数:
        img: 输入图像 (np.ndarray)
        pois: 单个坐标 [x, y] 或坐标列表 [[x1, y1], [x2, y2], ...]
        color: 十六进制颜色字符串，格式为 "RRGGBB-TolTolTol"，例如 "ffd900-101010"。
               - TolTolTol 是BGR三个通道的容差值（同样为十六进制）。
               - 如果没有提供容差，例如 "ffd900"，则默认为精确匹配 (容差为 "000000")。

    返回:
        如果所有点的颜色都匹配，则返回 True，否则返回 False。
    """
    try:
        if '-' in color:
            main_color_hex, tolerance_hex = color.split('-')
        else:
            main_color_hex = color
            tolerance_hex = "000000"

        target_bgr = _hex_to_bgr(main_color_hex)
        tolerance_bgr = _hex_to_bgr(tolerance_hex)
    except (ValueError, IndexError):
        # 无效的十六进制颜色或格式
        return False

    # 标准化输入坐标
    if not pois:
        return True  # 空坐标列表，视为匹配成功

    # 检查是否为单个坐标 e.g. [x, y]
    is_single_point = False
    if len(pois) == 2 and all(isinstance(p, (int, float, np.integer, np.floating)) for p in pois):
        is_single_point = True

    points = [pois] if is_single_point else pois

    for point in points:
        try:
            # 确保坐标是整数类型
            x, y = int(point[0]), int(point[1])
        except (ValueError, TypeError, IndexError):
            return False  # 坐标格式不正确

        # 检查坐标是否在图像边界内
        if not (0 <= y < img.shape[0] and 0 <= x < img.shape[1]):
            return False

        pixel_bgr = img[y, x]

        # 比较 B, G, R 三个通道
        for i in range(3):
            min_val = target_bgr[i] - tolerance_bgr[i]
            max_val = target_bgr[i] + tolerance_bgr[i]
            if not (min_val <= pixel_bgr[i] <= max_val):
                return False  # 任何一个点或一个通道不匹配，立即返回False

    return True


# 获取hsv
def GetHsv(img: np.ndarray, pois: Union[List[int], List[List[int]]]) -> Union[List[int], List[List[int]], None]:
    """获取图像中一个或多个点的HSV值。

    参数:
        img: 输入图像 (np.ndarray, BGR格式)
        pois: 单个坐标 [x, y] 或坐标列表 [[x1, y1], [x2, y2], ...]

    返回:
        如果输入为单个坐标，返回 [h, s, v] 列表。
        如果输入为坐标列表，返回 [[h1, s1, v1], [h2, s2, v2], ...] 列表。
        如果任何坐标无效或超出边界，则返回 None。
    """
    if not pois:
        return None

    is_single_point = False
    # 检查是否为单个坐标 e.g. [x, y]
    if len(pois) == 2 and all(isinstance(p, (int, float, np.integer, np.floating)) for p in pois):
        is_single_point = True

    points = [pois] if is_single_point else pois
    
    # 预先检查所有坐标的有效性
    for point in points:
        try:
            x, y = int(point[0]), int(point[1])
            if not (0 <= y < img.shape[0] and 0 <= x < img.shape[1]):
                return None  # 坐标超出边界
        except (ValueError, TypeError, IndexError):
            return None  # 坐标格式不正确

    # 将整个图像转换为HSV色彩空间以提高效率
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_values = []
    for point in points:
        x, y = int(point[0]), int(point[1])
        hsv_pixel = hsv_img[y, x]
        hsv_values.append([int(hsv_pixel[0]), int(hsv_pixel[1]), int(hsv_pixel[2])])

    if is_single_point:
        return hsv_values[0]
    
    return hsv_values


# 十六进制转rgb
def _hex_to_bgr(hex_str: str) -> Tuple[int, int, int]:
    """将RRGGBB十六进制字符串转换为BGR元组"""
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return b, g, r




