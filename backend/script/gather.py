import time
from ..global_var import api as G_api
from ..global_var import paras as G_para
from ..img_api.Img_load import ImageLoader
from ..img_api.Cv import MultiMatch, SingleMatch, CompareColor
from ..data.gather_info import gather_info



class Gather:
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
            'repair_time': time.time(),     # 维修装备时间
            'gather_name': None,            # 采集点名称
            'old_gather_name': None,        # 笔记采集点名称
            'need_repair': False,           # 是否需要维修装备
            'is_stuck': False,              # 是否卡住
            'last_gather_time':time.time(), # 上一次采集时间
            'stuck_out_mode':0,             # 卡住改出模式

        }
    
    # 加载图像数据
    def load_img_paras(self):
        imgs = ImageLoader()
        self.imgs = {
            # 主界面
            '主界面': ["主界面", imgs.主界面, {'method': 'Template', 'region': [58,619,350,92]}],
            # 关闭按钮
            '关闭按钮': ["关闭按钮", imgs.关闭按钮, {'method': 'Template', 'region': [1228,18,20,19],'color_sensitive': True}],
            # 切换职业
            '切换职业': ["切换职业", imgs.切换职业, {'method': 'Template', 'region': [575,200,127,48]}],
            # 采集笔记按钮
            '采集笔记按钮': ["采集笔记按钮", imgs.采集笔记按钮, {'method': 'Template', 'region': [1185,294,42,37]}],
            # 采集笔记ui
            '采集笔记ui': ["采集笔记ui", imgs.采集笔记ui, {'method': 'Template', 'region': [192,7,95,45]}],
            # 寻路按钮
            '寻路按钮': ["寻路按钮", imgs.寻路按钮, {'method': 'Template', 'region': [271,117,856,557]}],
            # 取消寻路按钮
            '取消寻路按钮': ["取消寻路按钮", imgs.取消寻路按钮, {'method': 'Template', 'region': [271,117,856,557]}],
            # 寻路中
            '寻路中': ["寻路中", imgs.寻路中, {'method': 'Template', 'region': [527,521,218,41]}],
            # 飞行中
            '飞行中': ["飞行中", imgs.飞行中, {'method': 'Template', 'region': [1098,511,44,31]}],
            # 可挖草
            '可挖草': ["可挖草", imgs.可挖草, {'method': 'Template', 'region': [718,334,33,37]}],
            # 可挖矿
            '可挖矿': ["可挖矿", imgs.可挖矿, {'method': 'Template', 'region': [717,328,35,37]}],
            # 获得力不足
            '获得力不足': ["获得力不足", imgs.获得力不足, {'method': 'Template', 'region': [479,62,153,183]}],
            # 角色按钮
            '角色按钮': ["角色按钮", imgs.角色按钮, {'method': 'Template', 'region': [961,19,40,36]}],
            # 角色ui
            '角色ui': ["角色ui", imgs.角色ui, {'method': 'Template', 'region': [102,4,82,48]}],
            # 切换攻击
            '切换攻击': ["切换攻击", imgs.切换攻击, {'method': 'Template', 'region': [1190,632,28,27]}],
            # 寻路中断
            '寻路中断': ["寻路中断", imgs.寻路中断, {'method': 'Template', 'region': [451,91,210,155]}],
            # 无法寻路
            '无法寻路': ["无法寻路", imgs.无法寻路, {'method': 'Template', 'region': [534,59,145,152]}],
            # 采集中无法寻路
            '采集中无法寻路': ["采集中无法寻路", imgs.采集中无法寻路, {'method': 'Template', 'region': [487,67,218,125]}],
            # 骑乘中
            '骑乘中': ["骑乘中", imgs.骑乘中, {'method': 'Template', 'region': [858,620,26,31]}],
            # 采矿工
            '采矿工': ["采矿工", imgs.采矿工, {'method': 'Template', 'region': [442,649,38,37]}],
            # 园艺工
            '园艺工': ["园艺工", imgs.园艺工, {'method': 'Template', 'region': [442,649,38,37]}],
        }

    # 更新采集列表
    def update_gather_list(self):
        if self.paras['gather_name'] and self.paras['gather_name'] in G_para.gathering_items and G_para.gathering_items[self.paras['gather_name']]['need'] > G_para.gathering_items[self.paras['gather_name']]['complete']:
            # self.logs.debug(f'当前采集物品【{self.paras["gather_name"]}】未采集完成，无需更新')
            return
        # 获取新的采集物品
        for key, value in G_para.gathering_items.items():
            if value['need'] > value['complete']:
                self.paras['gather_name'] = key
                self.logs.debug(f'更新当前采集物品为【{self.paras["gather_name"]}】')
                self.switch_job(gather_info[self.paras['gather_name']]['job'])
                return
        self.tips.success("采集列表已全部完成")
        self.time_sleep(10)
        self.paras['gather_name'] = None

    # 打开采集笔记并寻路
    def open_gather_note(self):
        result = MultiMatch(self.cap.screencap(), [self.imgs['采集笔记按钮'], self.imgs['寻路按钮'], self.imgs['取消寻路按钮'], self.imgs['飞行中']])
        # 飞行中先下坐骑
        if result.飞行中:
            self.auto_stuck_out('下坐骑')

        # 点击采集按钮并寻路
        elif result.采集笔记按钮:
            self.logs.debug(f'点击采集笔记按钮')
            self.auto_stuck_out('移动取消采集')
            self.mouse.click(result.采集笔记按钮.rect[0]+10, result.采集笔记按钮.rect[1]+10, 1)
            if SingleMatch(self.cap.screencap(), self.imgs['采集笔记ui']):
                if self.paras['old_gather_name'] != self.paras['gather_name']: # 是否重选
                    self.logs.debug(f'需要重选笔记中的采集物品')
                    self.choose_level(gather_info[self.paras['gather_name']]['level'])
                    self.choose_item(gather_info[self.paras['gather_name']]['note_index'])
                    self.paras['old_gather_name'] = self.paras['gather_name']
                self.mouse.click(880,440,2) # 点击采集点
            else:
                self.logs.debug("采集笔记ui未出现")
                return
        
        # 寻路
        elif result.寻路按钮:
            self.logs.debug(f'点击寻路按钮')
            if SingleMatch(self.cap.screencap(), self.imgs['切换职业']):    # 可能可以删了？
                self.logs.debug(f'寻路前需要切换职业')
                self.mouse.click(780,470, 1) # 切换职业
            self.mouse.click(result.寻路按钮.rect[0]+8, result.寻路按钮.rect[1]+8, 3) # 寻路
            # 判断寻路结束
            t_begin = time.time()
            xunlu_flag = False    # 是否寻路过
            zhongduan_flag = False
            while self.running:
                self.time_sleep(0.1)
                result = MultiMatch(self.cap.screencap(), [self.imgs['寻路中'], self.imgs['主界面'], self.imgs['可挖草'], self.imgs['可挖矿'], self.imgs['关闭按钮'], self.imgs['寻路中断'], self.imgs['无法寻路'], self.imgs['采集中无法寻路']])
                
                if result.寻路中 and not xunlu_flag:
                    xunlu_flag = True  
                
                elif result.采集中无法寻路:   # 解决还在采集，但是ui消失问题
                    self.mouse.click(1240, 30, 1)  # 点击返回
                    self.mouse.click(1240, 30, 1)  # 点击返回
                    self.auto_stuck_out('往后走')
                    break
                
                elif result.寻路中断:
                    self.logs.warning(f"寻路中断：尝试改出，模式{self.paras['stuck_out_mode']}")
                    if self.paras['stuck_out_mode'] == 0:
                        self.auto_stuck_out('往前飞一段')
                    elif self.paras['stuck_out_mode'] == 1:
                        self.auto_stuck_out('往后走')
                        # self.mouse.swipe([[230,545], [287,603]], 0.5, 2000)  # 右下移动前进
                    self.paras['stuck_out_mode'] = (self.paras['stuck_out_mode'] + 1) % 2
                    break
                
                elif result.无法寻路:
                    self.logs.warning("无法寻路，尝试改出")
                    self.auto_stuck_out('往后走')
                    break

                elif not xunlu_flag and time.time()-t_begin > 10:
                    self.logs.warning("寻路超时：未检测到寻路标志")
                    break
                
                elif time.time()-t_begin > 120:
                    self.logs.warning("寻路超时：寻路时间超过120秒")
                    break
                
                elif result.关闭按钮 and time.time()-t_begin > 5:
                    self.logs.warning("寻路超时：没有点击寻路按钮")
                    break
                
                elif result.可挖草 or result.可挖矿:
                    self.logs.warning("寻路结束：可采集物品")
                    break
                
                elif result.主界面 and xunlu_flag and not result.寻路中:
                    if zhongduan_flag:
                        self.logs.warning("寻路结束：正常结束")
                        break
                    else:   # 等待1秒检测寻路中断
                        self.time_sleep(1)
                        zhongduan_flag = True
                        continue

        # 点击取消寻路按钮
        elif result.取消寻路按钮:
            self.logs.debug(f'点击取消寻路按钮')
            self.mouse.click(result.取消寻路按钮.rect[0]+8, result.取消寻路按钮.rect[1]+8, 0.5)
            self.mouse.click(10, 30, 0.5)  # 点一下边缘，防止误触寻路
            self.mouse.click(1240, 30, 0.7)  # 点击返回
            self.mouse.click(913, 436, 2)  # 点击
            return

        # 关闭按钮
        elif not result.采集笔记按钮:
            self.auto_stuck_out('移动取消采集')
            if cash := SingleMatch(self.cap.screencap(), self.imgs['关闭按钮']):
                self.logs.debug(f'点击关闭按钮')
                self.mouse.click(cash.rect[0], cash.rect[1], 0.8)

    # 开始采集
    def start_gather(self):
        result = MultiMatch(self.cap.screencap(), [self.imgs['可挖草'], self.imgs['可挖矿']])
        if result.可挖草 or result.可挖矿:
            # 计算采集进度
            self.cal_progress()
            # 开始采集
            self.mouse.click(790, 350, 1.5)  # 点击采集
            t_begin = time.time()
            self.logs.debug(f'开始采集')
            self.paras['last_gather_time'] = time.time()
            self.paras['stuck_out_mode'] = 0 # 重置卡住改出模式
            gather_list = []    # 采集列表中的物品
            gather_list_len_old = len(gather_list) # 采集列表中的物品数量，用于判断是否滑动到底部
            gather_poi = None   # 需要采集的物品位置
            # 找到需要采集的位置
            while self.running:
                ocr_result = self.ocr.detect(self.cap.screencap(), [20,61,212,232])
                # 遍历ocr结果，找到需要采集的物品
                for key,value in ocr_result.items():
                    if key == self.paras['gather_name']:  # 找到了需要采集的物品
                        gather_poi = (370, int(value[1]+value[3]/2))
                        self.logs.debug(f'找到需要采集的物品坐标：{key},{gather_poi}')
                        break
                    elif key in gather_info and key not in gather_list:  # 不是需要采集的物品，但是是采集列表中的物品
                        gather_list.append(key)
                # 如果找到了需要采集的物品，则跳出循环，否则滑动，重新检测
                if gather_poi:
                    break
                elif len(gather_list) != gather_list_len_old:
                    self.mouse.swipe([[195,280], [195,80]], 2, 1500)  # 滑动
                    gather_list_len_old = len(gather_list)
                else:
                    self.logs.warning("采集列表中未找到需要采集的物品")
                    # self.mouse.swipe([[230,545], [230,370]], 2, 3000)  # 通过移动取消采集
                    self.auto_stuck_out('移动取消采集')
                    break
                self.time_sleep(0.1)
            # 连按采集
            while self.running and gather_poi:
                self.time_sleep(0.1)
                result = MultiMatch(self.cap.screencap(), [self.imgs['主界面'], self.imgs['获得力不足']])
                if result.获得力不足:
                    self.logs.error("需要维修装备")
                    self.paras['need_repair'] = True
                    self.auto_stuck_out('移动取消采集')
                    # self.mouse.swipe([[230,545], [230,370]], 2, 3000)  # 通过移动取消采集
                    return
                elif not result.主界面:
                    self.mouse.click(*gather_poi)
                elif result.主界面 and time.time()-t_begin>5:
                    self.logs.debug("采集完成")
                    return
                if time.time()-t_begin > 60:
                    # 现在已经不卡UI了
                    self.auto_stuck_out('移动取消采集')
                    # self.mouse.swipe([[230,545], [230,370]], 2, 3000)  # 通过移动取消采集
                    self.logs.debug("采集超时")
                    return

    # 获取采集进度
    def cal_progress(self):
        if self.paras['gather_name'] in G_para.gathering_items:
            current_time = time.time()  
            # 如果是首次采集该物品，记录开始时间
            if 'start_time' not in G_para.gathering_items[self.paras['gather_name']]:
                G_para.gathering_items[self.paras['gather_name']]['start_time'] = current_time
            
            # 增加完成数量
            G_para.gathering_items[self.paras['gather_name']]['complete'] += 1
            
            # 如果采集完成，记录结束时间
            if G_para.gathering_items[self.paras['gather_name']]['complete'] >= G_para.gathering_items[self.paras['gather_name']]['need']:
                G_para.gathering_items[self.paras['gather_name']]['end_time'] = current_time
            
            # 计算采集速度（每分钟采集数量）
            start_time = G_para.gathering_items[self.paras['gather_name']]['start_time']
            complete_count = G_para.gathering_items[self.paras['gather_name']]['complete']
            
            # 计算已用时间（分钟）
            elapsed_minutes = (current_time - start_time) / 60
            
            if elapsed_minutes > 0:
                # 计算每分钟完成数量
                speed = complete_count / elapsed_minutes
                G_para.gathering_items[self.paras['gather_name']]['num_per_min'] = round(speed, 2)

    # 采集笔记等级选择
    def choose_level(self, level):
        self.logs.debug(f'开始选择采集笔记等级')
        level_poi = [[268,190],[268,230],[268,270],[268,310],[268,350],[268,390],[268,430],[268,460]]  # 等级选择点
        self.mouse.click(268,150,0.5) # 点击等级列表
        self.mouse.click(*level_poi[0], 0.5)  # 刷新次序
        self.mouse.click(268,150,0.5) # 点击等级列表
        if 1 <= level <= 5:
            self.mouse.click(*level_poi[0], 0.5)
        elif 6 <= level <= 10:
            self.mouse.click(*level_poi[1], 0.5)
        elif 11 <= level <= 15:
            self.mouse.click(*level_poi[2], 0.5)
        elif 16 <= level <= 20:
            self.mouse.click(*level_poi[3], 0.5)
        elif 21 <= level <= 25:
            self.mouse.click(*level_poi[4], 0.5)
        elif 26 <= level <= 30:
            self.mouse.click(*level_poi[5], 0.5)
        elif 31 <= level <= 35:
            self.mouse.click(*level_poi[6], 0.5)
        elif 36 <= level <= 40:
            self.mouse.swipe([level_poi[6], [level_poi[6][0], level_poi[6][1]-40]],0.5)
            self.mouse.click(*level_poi[6], 0.5)
        elif 41 <= level <= 45:
            self.mouse.swipe([level_poi[6], [level_poi[6][0], level_poi[6][1]-40*2]],0.5)
            self.mouse.click(*level_poi[6], 0.5)
        elif 46 <= level <= 50:
            self.mouse.swipe([level_poi[6], [level_poi[6][0], level_poi[6][1]-40*3]],0.5)
            self.mouse.click(*level_poi[7], 0.5)

    # 采集笔记物品选择
    def choose_item(self, id):
        self.logs.debug(f'开始选择采集笔记物品')
        item_poi = [[350,215],[350,300],[350,385],[350,470],[350,555],[350,640]]
        if id == 1:
            self.mouse.click(*item_poi[0], 0.5)
        elif id == 2:
            self.mouse.click(*item_poi[1], 0.5)
        elif id == 3:
            self.mouse.click(*item_poi[2], 0.5)
        elif id == 4:
            self.mouse.click(*item_poi[3], 0.5)
        elif id == 5:
            self.mouse.click(*item_poi[4], 0.5)
        elif id == 6:
            self.mouse.click(*item_poi[5], 0.5)
        elif id >= 7:
            rounds = (id-6)//6
            for _ in range(rounds):
                self.mouse.swipe([item_poi[5],[item_poi[5][0], item_poi[5][1]-85*3], [item_poi[5][0], item_poi[5][1]-85*6-5]],0.5,1000)

            if id % 6 != 0:
                self.mouse.swipe([item_poi[5], [item_poi[5][0], item_poi[5][1]-85*(id % 6)]],0.5)
            self.mouse.click(*item_poi[5], 0.5)

    # 维修装备
    def repair_equipment(self):
        result = MultiMatch(self.cap.screencap(), [self.imgs['角色按钮'], self.imgs['角色ui'], self.imgs['关闭按钮']])
        if result.角色按钮:
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
            self.paras['need_repair'] = False
            self.paras['repair_time'] = time.time()

        elif not result.角色按钮 and not result.角色ui and result.关闭按钮:
            self.logs.debug(f'点击关闭按钮')
            self.mouse.click(result.关闭按钮.rect[0], result.关闭按钮.rect[1], 1)

        elif self.paras['need_repair']:
            self.logs.debug("可能卡住UI")
            self.paras['is_stuck'] = True

    # 切换职业
    def switch_job(self, job):
        result = MultiMatch(self.cap.screencap(), [self.imgs['切换攻击'], self.imgs['关闭按钮'], self.imgs['采矿工'], self.imgs['园艺工']])
        if result.切换攻击:
            if (result.采矿工 and job == '采矿工') or (result.园艺工 and job == '园艺工'):
                self.logs.debug(f'当前职业为{job}，无需切换')
                return
            self.logs.debug(f'开始切换职业为{job}')
            self.auto_stuck_out('移动取消采集')
            self.mouse.click(463,668,0.8)  # 点击切换职业
            self.mouse.click(1139,669,0.8)  # 点击生产职业
            if job == '采矿工':
                self.mouse.click(1155,143,1.5)  # 点击采矿工
            elif job == '园艺工':
                self.mouse.click(1155,200,1.5)  # 点击园艺工
        elif result.关闭按钮:
            self.logs.debug(f'点击关闭按钮')
            self.mouse.click(result.关闭按钮.rect[0], result.关闭按钮.rect[1], 0.8)
            self.switch_job(job)

    # 卡顿自动改出
    def auto_stuck_out(self, mode_name):
        # 移动取消采集
        if mode_name == '移动取消采集':
            if CompareColor(self.cap.screencap(), [[447, 48],[450, 48],[455, 48]], 'ffffff-020202'):
                self.mouse.swipe([[230,545], [230,370]], 1, 1500)  # 通过移动取消采集
                self.mouse.click(774, 464, 2)   # 收藏品退出确定
        elif mode_name == '解决卡住':
            self.auto_stuck_out('移动取消采集')
            self.mouse.click(1165, 72, 2.5) # 地图
            self.mouse.click(450, 30, 1)    # 下拉菜单
            self.mouse.click(340, 110, 2.5) # 黑衣森林
            self.mouse.click(547, 353, 1)   # 点水晶
            self.mouse.click(665, 295, 1)   # 传送
            self.time_sleep(5)
            self.paras['is_stuck'] = False
        elif mode_name == '下坐骑':
            t_begin = time.time()
            self.mouse.click(963, 646, 1)       # 下坐骑
            while self.running:
                if SingleMatch(self.cap.screencap(), self.imgs['骑乘中']):
                    if time.time()-t_begin >= 8:
                        self.logs.warning("下坐骑超时")
                        self.paras['is_stuck'] = True
                        break
                else:
                    break
                self.time_sleep(0.1)
        elif mode_name == '往后走':
            self.mouse.swipe([[230,545], [230,640]], 1, 4000)  # 往后走
            self.mouse.click(774, 464, 0.5)   # 收藏品退出确定
        elif mode_name == '往前飞一段':
            if not SingleMatch(self.cap.screencap(), self.imgs['骑乘中']):
                self.mouse.click(963, 646, 3.5)       # 上坐骑
            self.mouse.click(1200, 510, 0.3, duration=1200)       # 飞起来
            self.mouse.swipe([[230,545], [230,430]], 0.3, 800)  # 固定前进
            self.mouse.click(963, 646, 1.2)       # 下坐骑











    # 刷新状态
    def refresh_status(self):
        if time.time() - self.paras['last_gather_time'] > 240:
            self.logs.warning("采集超时：超过240秒未采集")
            self.paras['last_gather_time'] = time.time()
            self.paras['is_stuck'] = True
            return
        if time.time() - self.paras['repair_time'] > 60*30:
            self.logs.warning("采集时间超过30分钟，维修装备")
            self.paras['need_repair'] = True
            return





    def run(self):
        while self.running:
            try:
                self.refresh_status()
                self.update_gather_list()
                if self.paras['gather_name']:
                    if not self.paras['need_repair'] and not self.paras['is_stuck']:
                        self.open_gather_note()
                        self.start_gather()
                    if self.paras['need_repair'] and not self.paras['is_stuck']:
                        self.repair_equipment()
                    if self.paras['is_stuck']:
                        self.auto_stuck_out('解决卡住')
            except Exception as e:
                self.logs.error(f"采集过程中出错: {e}")
            self.time_sleep(0.1)


    def stop(self):
        self.running = False


    def time_sleep(self, time_value):
        t_begin = time.time()
        while(self.running):
            time.sleep(0.01)
            if time.time()-t_begin>time_value:
                return

