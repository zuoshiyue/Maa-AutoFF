import time
from ..global_var import api as G_api
from ..global_var import paras as G_para
from ..img_api.Img_load import ImageLoader
from ..img_api.Cv import MultiMatch, SingleMatch, CompareColor



class Fish:
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
            # 'is_fishing': False,     # 是否正在钓鱼
            'fish_nums': 0,          # 钓鱼次数
            'repair_time': time.time(), # 维修装备时间
            'submit_time': time.time(), # 提交收藏品时间
        }


    def load_img_paras(self):
        imgs = ImageLoader()
        self.imgs = {
            # 开始钓鱼
            '开始钓鱼': ["开始钓鱼", imgs.开始钓鱼, {'method': 'Template', 'region': [1085,548,71,49]}],
            # 结束钓鱼
            '结束钓鱼': ["结束钓鱼", imgs.结束钓鱼, {'method': 'Template', 'region': [1085,549,58,43]}],
            # 钓鱼收藏品确认
            '钓鱼收藏品确认': ["钓鱼收藏品确认", imgs.钓鱼收藏品确认, {'method': 'Template', 'region': [769,514,106,49]}],
            # 提交收藏品
            '提交收藏品': ["提交收藏品", imgs.提交收藏品, {'method': 'Template', 'region': [1060,593,82,40]}],
            # 以小钓大
            '以小钓大': ["以小钓大", imgs.以小钓大, {'method': 'Template', 'region': [1090,398,53,50], 'color_sensitive': True}],

            # 角色按钮
            '角色按钮': ["角色按钮", imgs.角色按钮, {'method': 'Template', 'region': [961,19,40,36]}],
            # 角色ui
            '角色ui': ["角色ui", imgs.角色ui, {'method': 'Template', 'region': [102,4,82,48]}],
            # 关闭按钮
            '关闭按钮': ["关闭按钮", imgs.关闭按钮, {'method': 'Template', 'region': [1228,18,20,19],'color_sensitive': True}],

        }


    # 钓鱼
    def start_fishing(self):
        result = MultiMatch(self.cap.screencap(), [self.imgs['开始钓鱼'],self.imgs['结束钓鱼'], self.imgs['以小钓大']])
        if result.开始钓鱼:
            self.logs.debug("开始钓鱼")
            self.paras['fish_nums'] += 1
            self.logs.debug(f"钓鱼次数：{self.paras['fish_nums']}")
            while self.running:
                if SingleMatch(self.cap.screencap(), self.imgs['结束钓鱼']):
                    return
                if result.以小钓大 and G_para.fish_settings['small_to_big']:
                    self.logs.debug("以小钓大")
                    self.mouse.click(result.以小钓大.rect[0]+8, result.以小钓大.rect[1]+8, 1)
                else:
                    self.mouse.click(result.开始钓鱼.rect[0]+8, result.开始钓鱼.rect[1]+8, 2)

        elif result.结束钓鱼:
            if not CompareColor(self.cap.screencap(), [861,371], 'fcd795-101010'):
                self.logs.debug("结束钓鱼")
                self.mouse.click(1070,640,0.2) # 点一下坐下，取消后摇
                self.mouse.click(result.结束钓鱼.rect[0]+8, result.结束钓鱼.rect[1]+8, 2)
                while self.running:
                    cash = MultiMatch(self.cap.screencap(), [self.imgs['开始钓鱼'],self.imgs['钓鱼收藏品确认']])
                    if cash.开始钓鱼:
                        return
                    elif cash.钓鱼收藏品确认:
                        self.logs.debug("点击钓鱼收藏品确认")
                        self.mouse.click(cash.钓鱼收藏品确认.rect[0]+8, cash.钓鱼收藏品确认.rect[1]+8, 1)
                    else:
                        self.time_sleep(1)

        else:
            self.logs.warning("未找到钓鱼按钮")
            self.tips.warning("请手动切换钓鱼职业并前往钓鱼点")
            self.time_sleep(5)


    # 维修装备-37分钟
    def repair_equipment(self):
        if time.time()-self.paras['repair_time'] > 60*37 and G_para.fish_settings['need_repair']:
            result = MultiMatch(self.cap.screencap(), [self.imgs['角色按钮'], self.imgs['角色ui'], self.imgs['关闭按钮']])
            if result.角色按钮:
                self.mouse.swipe([[230,545], [300,545]], 3, 1000)   # 取消钓鱼
                self.mouse.click(result.角色按钮.rect[0], result.角色按钮.rect[1], 1.5)
                self.repair_equipment() # 去检测角色ui界面

            elif result.角色ui:
                self.logs.debug(f'开始维修装备')
                self.mouse.click(143,177,1)   # 点击装备1
                self.mouse.click(1110,130,1)  # 点击装备2
                self.mouse.click(400,660,1)   # 点击三点
                self.mouse.click(480,600,1)   # 点击维修
                self.mouse.click(640,600,2)   # 点击全部修理
                self.mouse.click(1183,85,1)   # 点击返回
                self.mouse.click(1240,30,1)   # 点击返回
                self.mouse.click(1240,30,1)   # 点击返回
                self.logs.debug("维修装备完成")
                self.paras['repair_time'] = time.time()

            elif not result.角色按钮 and not result.角色ui and result.关闭按钮:
                self.logs.debug(f'点击关闭按钮')
                self.mouse.click(result.关闭按钮.rect[0], result.关闭按钮.rect[1], 1)


    # 提交收藏品-15分钟
    def submit_collection(self):
        if time.time()-self.paras['submit_time'] > 60*15 and G_para.fish_settings['need_submit']:
            if SingleMatch(self.cap.screencap(), self.imgs['开始钓鱼']):
                self.mouse.swipe([[230,545], [300,545]], 3, 1000)   # 取消钓鱼
                self.mouse.click(1060,290,1.5)  # 打开提交界面
                while self.running:
                    if SingleMatch(self.cap.screencap(), self.imgs['提交收藏品']):
                        self.mouse.click(1100,615,1)  # 交换
                    else:
                        self.mouse.click(1240,30,1)   # 点击返回
                        self.paras['submit_time'] = time.time()  # 记录提交时间
                        return



    def run(self):
        while self.running:
            self.start_fishing()
            self.repair_equipment()
            self.submit_collection()  # 提交收藏品
            self.time_sleep(0.1)



    def stop(self):
        self.running = False



    def time_sleep(self, time_value):
        t_begin = time.time()
        while(self.running):
            time.sleep(0.01)
            if time.time()-t_begin>time_value:
                return




