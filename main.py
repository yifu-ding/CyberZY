import numpy as np
import time 
import requests
from openai import OpenAI

OPENAI_API_KEY = "your openai api-key"

def get_yao(seed=0): 
    
    np.random.seed(seed)

    start = 50  # 大衍之数五十
    start -= 1  # 其用四十有九（减去的1称为不易）
    
    total = start

    for i in range(3):

        # 分二：一分为二，分为“天地”
        tian = np.random.randint(4, total-4) # [4, total-4)
        di = start - tian
        di -= 1  # 挂一：从“地”里取出一个作为人

        # 揲四：四个为一组（春夏秋冬，元亨利贞）
        tian_yushu = tian % 4
        di_yushu = di % 4
        # 归奇：将余数取出，余数为0则取4
        if tian_yushu == 0: tian_yushu = 4
        if di_yushu == 0: di_yushu = 4

        yushu = tian_yushu + di_yushu 
        if i == 0: yushu += 1  # 加上挂一

        assert (i == 0 and (yushu == 5 or yushu == 9)) \
                or (i == 1 and (yushu == 4 or yushu == 8)) \
                or (i == 2 and (yushu == 4 or yushu == 8))
        
        total = total - yushu

    group_num = total // 4
    assert group_num == 6 or group_num == 7 or group_num == 8 or group_num == 9

    return group_num



class GuaMing():

    # 八卦
    # ☰乾  	☱兑  	☲离  	☳震  
    # ☴巽  	☵坎  	☶艮  	☷坤  

    gua_8_dict_long = {
        "111": "☰ 三连为“乾”，表示天",
        "011": "☱ 上缺为“兑”，表示泽",
        "101": "☲ 中虚为“离”，表示火",
        "001": "☳ 仰盂为“震”，表示雷",
        "110": "☴ 下断为“巽”，表示风",
        "010": "☵ 中满为“坎”，表示水",
        "100": "☶ 覆碗为“艮”，表示山",
        "000": "☷ 六断为“坤”，表示地",
    }

    gua_8_dict_short = {
        "111": "天",
        "011": "泽",
        "101": "火",
        "001": "雷",
        "110": "风",
        "010": "水",
        "100": "山",
        "000": "地",
    }

    # 六十四卦
    # ䷀乾  	䷁坤  	䷂屯  	䷃蒙  	䷄需  	䷅讼  	䷆师  	䷇比  
    # ䷈小畜 	䷉履  	䷊泰  	䷋否  	䷌同人 	䷍大有 	䷎谦  	䷏豫  
    # ䷐随  	䷑蛊  	䷒临  	䷓观  	䷔噬嗑 	䷕贲  	䷖剥  	䷗复  
    # ䷘无妄 	䷙大畜 	䷚颐  	䷛大过 	䷜坎  	䷝离  	䷞咸  	䷟恒  
    # ䷠遁  	䷡大壮 	䷢晋  	䷣明夷 	䷤家人 	䷥睽  	䷦蹇  	䷧解  
    # ䷨损  	䷩益  	䷪夬  	䷫姤  	䷬萃  	䷭升  	䷮困  	䷯井  
    # ䷰革  	䷱鼎  	䷲震  	䷳艮  	䷴渐  	䷵归妹 	䷶丰  	䷷旅  
    # ䷸巽  	䷹兑  	䷺涣  	䷻节  	䷼中孚 	䷽小过 	䷾既济 	䷿未济  

    gua_64_dict = {
        "111111": "乾", "000000": "坤", "010001": "屯", "100010": "蒙",
        "010111": "需", "111010": "讼", "000010": "师", "010000": "比",
        "110111": "小畜", "111011": "履", "000111": "泰", "111000": "否",
        "111101": "同人", "101111": "大有", "000100": "谦", "001000": "豫",
        "011001": "随", "100110": "蛊", "000011": "临", "110000": "观",
        "101001": "噬嗑", "100101": "贲", "100000": "剥", "000001": "复",
        "111001": "无妄", "100111": "大畜", "100001": "颐", "011110": "大过", 
        "010010": "坎", "101101": "离", "011100": "咸", "001110": "恒", 
        "111100": "遁", "001111": "大壮", "101000": "晋", "000101": "明夷",
        "110101": "家人", "101011": "睽", "010100": "蹇", "001010": "解",
        "100011": "损", "110001": "益", "011111": "夬", "111110": "姤", 
        "011000": "萃", "000110": "升", "011010": "困", "010110": "井", 
        "011101": "革", "101110": "鼎", "001001": "震", "100100": "艮", 
        "110100": "渐", "001011": "归妹", "001101": "丰", "101100": "旅",
        "110110": "巽", "011011": "兑", "110010": "涣", "010011": "节", 
        "110011": "中孚", "001100": "小过", "010101": "既济", "101010": "未济"
    }

def get_guaming_by_liuyao(liuyao):
    # liuyao: idx=0: 五爻，idx=5: 初爻
    
    assert len(liuyao) == 6
    if liuyao == '111111': return "乾为天"
    elif liuyao == '000000': return "坤为地"
    else:
        guaming = GuaMing.gua_8_dict_short[liuyao[:3]] + \
            GuaMing.gua_8_dict_short[liuyao[3:]] + GuaMing.gua_64_dict[liuyao]
        return guaming
    

def get_guaming(num_list):
    # import pdb; pdb.set_trace()
    yao_list = [yao % 2 for yao in num_list]  # 1为阳爻，0为阴爻 # idx=0: 初爻，idx=5: 五爻
    yao_list = yao_list[::-1]  # idx=0: 五爻，idx=5: 初爻 
    liuyao = ""
    for i in yao_list: liuyao += str(i)
    return get_guaming_by_liuyao(liuyao)


def get_shangbagua(num_list): # 上八卦
    yao_list = [yao % 2 for yao in num_list]  # 1为阳爻，0为阴爻 # idx=0: 初爻，idx=5: 五爻
    yao_list = yao_list[::-1]  # idx=0: 五爻，idx=5: 初爻 
    liuyao = ""
    for i in yao_list: liuyao += str(i)
    return GuaMing.gua_8_dict_long[liuyao[:3]]


def get_xiabagua(num_list): # 下八卦
    yao_list = [yao % 2 for yao in num_list]  # 1为阳爻，0为阴爻 # idx=0: 初爻，idx=5: 五爻
    yao_list = yao_list[::-1]  # idx=0: 五爻，idx=5: 初爻 
    liuyao = ""
    for i in yao_list: liuyao += str(i)
    return GuaMing.gua_8_dict_long[liuyao[3:]]


def print_gua(num_list):
    
    # 6 老阴，9 老阳，7 少阳，8 少阴
    for i in range(5, -1, -1):  # 易气由下生
        yao = num_list[i]
        if   yao == 6: print("____  ____")
        elif yao == 7: print("__________")
        elif yao == 8: print("____  ____")
        elif yao == 9: print("__________")


def get_bian_gua(num_list):
    bian_gua = []
    # 少阳少阴不变，老阳老阴变
    for yao in num_list:
        if yao == 7: bian_gua.append(7)  
        elif yao == 8: bian_gua.append(8)
        elif yao == 9: bian_gua.append(8)
        elif yao == 6: bian_gua.append(7)
    bian_gua_position = [a!=b for a, b in zip(num_list, bian_gua)]
    # print(bian_gua_position)
    return bian_gua, bian_gua_position


def get_bianyao_prompt_naive(bian_gua_position):
    _dict = {
        0: "以本卦卦辞断",
        1: "以本卦变爻爻辞断",
        2: "以本卦两个爻辞断，但以上者为主",
        3: "以本卦与变卦卦辞断；本卦为体，变卦为用（本卦为主，变卦为辅）",
        4: "以变卦之两不变爻爻辞断，但以下者为主",
        5: "以变卦之不变爻爻辞断",
        6: "以变卦之卦辞断，乾坤两卦则以「用」辞断"
    }
   
    accumulate = sum(bian_gua_position)
    # prompt1 = _dict[accumulate]
    # get_bianyao_prompt_detail(bian_gua_position)
    return _dict[accumulate]


def get_prompt():
    
    # 起卦
    print("---- 三变生爻，六爻为卦 ----")
    ben_gua = []  # 本卦
    for i in range(6):  # 六爻成卦
        seed = int(time.time()) + i
        ben_gua.append(get_yao(seed=seed))

    assert len(ben_gua) == 6

    print("本卦：")
    print_gua(ben_gua)
    print(get_guaming(ben_gua))

    print("")

    print("变卦：")
    bian_gua, bian_gua_position = get_bian_gua(ben_gua)
    print_gua(bian_gua)
    print(get_guaming(bian_gua))

    print("")
    
    prompt_dict = {
        "bengua": get_guaming(ben_gua),
        "biangua": get_guaming(bian_gua),
        "bianyao": get_bianyao_prompt_naive(bian_gua_position),
        "question": input("想问的问题是："),
    }
    
    prompt = "根据六爻帮我算卦，本卦是"+prompt_dict["bengua"] + \
            "，变卦是"+prompt_dict["biangua"]+"，"+prompt_dict['bianyao'] + \
            "。我想问的问题是，"+prompt_dict['question']

    return prompt
    

def ask_gpt(prompt):

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://api.openai.com/v1/chat/completions"
    )

    messages = [{'role': 'user','content': prompt},]
    
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    print("\n解卦：")
    print(completion.choices[0].message.content)
    
    # import pdb; pdb.set_trace()
    
prompt = get_prompt()
print(prompt)

ask_gpt(prompt)










