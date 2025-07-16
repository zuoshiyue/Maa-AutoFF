
import time
from ..global_var import api as G_api
from ..global_var import paras as G_para
from ..img_api.Img_load import ImageLoader
from ..img_api.Cv import MultiMatch, SingleMatch, CompareColor




class GoldSaucer:
    def __init__(self):
        self.running = True
        self.tips = G_api.tips_api
        self.logs = G_api.logs_api
        self.ocr = G_para.emulator_api['ocr']
        self.cap = G_para.emulator_api['cap']
        self.mouse = G_para.emulator_api['mouse']
        self.keyboard = G_para.emulator_api['keyboard']
        self.imgs = None
        self.load_img_paras()
        self.paras = {
            'ball_nums': 1,    # 单场抓球次数
            'ball_cash': None,    # 球位置存储
        }

    def load_img_paras(self):
        imgs = ImageLoader()
        self.imgs = {
            # 开始金蝶小游戏
            '开始金蝶小游戏': ["开始金蝶小游戏", imgs.开始金蝶小游戏, {'method': 'Template', 'region': [711,323,72,53]}],
            # 金蝶小游戏确认
            '金蝶小游戏确认': ["金蝶小游戏确认", imgs.金蝶小游戏确认, {'method': 'Template', 'region': [734,434,84,44]}],
            # 莫古翻倍挑战
            '莫古翻倍挑战': ["莫古翻倍挑战", imgs.莫古翻倍挑战, {'method': 'Template', 'region': [770,525,107,41]}],
            # 莫古抓球再战
            '莫古抓球再战': ["莫古抓球再战", imgs.莫古抓球再战, {'method': 'Template', 'region': [1090,639,90,48]}],
            
            
            # 莫古红球
            '莫古红球': ["莫古红球", imgs.莫古红球, {'method': 'Template', 'region': [828,250,334,292], 'color_sensitive': True}],
            # 莫古紫球
            '莫古紫球': ["莫古紫球", imgs.莫古紫球, {'method': 'Template', 'region': [828,250,334,292], 'color_sensitive': True}],
            # 莫古蓝球
            '莫古蓝球': ["莫古蓝球", imgs.莫古蓝球, {'method': 'Template', 'region': [828,250,334,292], 'color_sensitive': True}],
            # 抓球左
            '抓球左': ["抓球左", imgs.抓球左, {'method': 'Template', 'region': [876,554,85,36], 'color_sensitive': True}],
            # 抓球右
            '抓球右': ["抓球右", imgs.抓球右, {'method': 'Template', 'region': [1030,553,71,39], 'color_sensitive': True}],

        }





    def auto_play(self):
        result = MultiMatch(self.cap.screencap(), [self.imgs['开始金蝶小游戏'], self.imgs['金蝶小游戏确认'], self.imgs['莫古翻倍挑战'], self.imgs['莫古抓球再战'], self.imgs['抓球左'], self.imgs['抓球右']])

        if result.开始金蝶小游戏:
            self.mouse.click(result.开始金蝶小游戏.rect[0], result.开始金蝶小游戏.rect[1], 0.5)
        elif result.金蝶小游戏确认:
            self.mouse.click(result.金蝶小游戏确认.rect[0], result.金蝶小游戏确认.rect[1], 0.5)
            self.paras['ball_nums'] = 1
        elif result.莫古翻倍挑战:
            self.mouse.click(result.莫古翻倍挑战.rect[0], result.莫古翻倍挑战.rect[1], 0.5)
            self.paras['ball_nums'] += 1
        elif result.莫古抓球再战:
            self.mouse.click(result.莫古抓球再战.rect[0], result.莫古抓球再战.rect[1], 0.5)
            self.paras['ball_nums'] = 1
        elif result.抓球左:
            if self.paras['ball_nums'] == 1:
                self.time_sleep(1)
            else:
                self.time_sleep(0.3)
            cash = SingleMatch(self.cap.screencap(), self.imgs['莫古红球']) or SingleMatch(self.cap.screencap(), self.imgs['莫古紫球']) or SingleMatch(self.cap.screencap(), self.imgs['莫古蓝球'])
            self.paras['ball_cash'] = cash
            if cash:
                if self.paras['ball_nums'] <= 2:
                    x_time = int(((cash.rect[0]+cash.rect[2]/2)-(853))*14.71)
                else:
                    x_time = int(((cash.rect[0]+cash.rect[2]/2)-(846))*10.07)
                if x_time < 400:
                    x_time = 50
                self.mouse.click(920, 568, 0.5, duration=x_time)
        elif result.抓球右:
            if cash := self.paras['ball_cash']:
                if self.paras['ball_nums'] <= 2:
                    y_time = int(((cash.rect[1]+cash.rect[3]/2)-290)*16.67)
                else:
                    y_time = int(((cash.rect[1]+cash.rect[3]/2)-290)*10.99)
                self.mouse.click(1063, 577, 0.5, duration=y_time)

        


    def run(self):
        while self.running:
            self.auto_play()
            self.time_sleep(0.1)
    

    def stop(self):
        self.running = False


    def time_sleep(self, time_value):
        t_begin = time.time()
        while(self.running):
            time.sleep(0.01)
            if time.time()-t_begin>time_value:
                return



