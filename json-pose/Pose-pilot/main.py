import math
import json
import requests
import os
import random
import time 
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from speaker.ip_speaker import send_tts

app = Flask(__name__, static_folder='static')

# ========== 关键点数据 ==========
# 头部摆正，双眼平视，调整坐姿，守护脊柱。
JSON_KEYPOINTS = [
    120.8515625,0.986328125,504.84375,
    107.578125,0.94384765625,493.59375,
    108.515625,0.9638671875,510.46875,
    110.7421875,0.63916015625,483.75,
    112.8515625,0.84033203125,518.4375,
    137.4609375,0.994140625,476.953125,
    140.625,0.99560546875,529.21875,
    169.6875,0.97509765625,476.71875,
    177.421875,0.986328125,524.53125,
    186.09375,0.96630859375,502.03125,
    192.1875,0.98095703125,518.90625,
    190.78125,0.9970703125,488.4375,
    193.125,0.99755859375,539.0625,
    209.0625,0.9931640625,491.25,
    210.234375,0.994140625,540.0,
    273.75,0.9697265625,489.375,
    275.15625,0.97119140625,344.862890625,
]

# 头部摆正，双眼平视，调整座椅，定时起身动一动！
JSON_KEYPOINTS = [
    125.3215625, 0.989328125, 502.14375,   # 头部关键点（接近理想）
    110.178125, 0.97384765625, 495.29375,   # 颈部关键点
    112.515625, 0.9688671875, 508.66875,    # 颈部另一关键点
    115.7421875, 0.83916015625, 485.15,     # 面部关键点
    118.8515625, 0.86033203125, 516.4375,   # 面部关键点
    139.4609375, 0.992140625, 478.953125,   # 左肩
    142.625, 0.99460546875, 527.21875,      # 右肩（与左肩平衡）
    171.6875, 0.97809765625, 477.71875,     # 左肘
    179.421875, 0.988328125, 522.53125,     # 右肘（与左肘对称）
    188.09375, 0.96930859375, 503.03125,    # 左手
    194.1875, 0.98295703125, 517.90625,     # 右手
    192.78125, 0.9960703125, 489.4375,      # 左腰
    195.125, 0.99655859375, 537.0625,       # 右腰（对称）
    211.0625, 0.9921640625, 492.25,         # 左髋
    212.234375, 0.993140625, 539.0,         # 右髋（对称）
    275.75, 0.9727265625, 490.375,          # 左膝
    277.15625, 0.97319140625, 345.862890625,# 右膝
]

# 看起来你坐得太直了，身体有点僵硬哦！试着稍微放松，让身体自然前倾一点点，颈部也稍微抬起，与屏幕保持适当距离，这样坐会更舒服，也能减少颈椎压力哦！
# JSON_KEYPOINTS = [
#     100.8359375, 0.99658203125, 320.862890625,
#     506.251171875, 0.98486328125, 340.04609375,
#     135.65078125, 0.98095703125, 300.278125,
#     139.83984375, 0.83740234375, 360.21953125,
#     104.837890625, 0.81640625, 280.29765625,
#     133.414453125, 0.9892578125, 464.745703125,
#     137.7578125, 0.9912109375, 402.406640625,
#     131.153125, 0.9873046875, 517.09453125,
#     149.34453125, 0.9892578125, 521.090625,
#     138.209765625, 1.0, 509.501953125,
#     184.701171875, 1.0, 509.501953125,
#     174.40859375, 0.9990234375, 703.3125,
#     143.28984375, 0.9990234375, 704.9109375,
#     113.2078125, 0.9873046875, 890.3296875,
#     104.07734375, 0.9873046875, 529.21875,
#     ]

# #“调整头部位置，平衡肩膀，坐直身体哦！
# JSON_KEYPOINTS = [
#     120.8515625, 0.986328125, 600.84375,    # 头部低头（y远大于理想，接近胸部）
#     107.578125, 0.94384765625, 580.59375,   # 颈部前倾过度
#     108.515625, 0.9638671875, 605.46875,    # 颈部前倾过度#
#     110.7421875, 0.63916015625, 570.75,      # 面部贴近胸部
#     112.8515625, 0.84033203125, 610.4375,   # 面部贴近胸部#
#     137.4609375, 0.994140625, 476.953125,   # 肩膀耸起#
#     140.625, 0.99560546875, 529.21875,      # 肩膀耸起
#     169.6875, 0.97509765625, 476.71875,     # 左肘弯曲过度
#     177.421875, 0.986328125, 524.53125,     # 右肘弯曲过度
#     186.09375, 0.96630859375, 502.03125,    # 左手悬空
#     192.1875, 0.98095703125, 518.90625,     # 右手悬空
#     190.78125, 0.9970703125, 488.4375,      # 腰部弯曲
#     193.125, 0.99755859375, 539.0625,       # 腰部弯曲
#     209.0625, 0.9931640625, 491.25,         # 髋部前倾
#     210.234375, 0.994140625, 540.0,         # 髋部前倾
#     273.75, 0.9697265625, 489.375,          # 膝盖并拢过紧
#     275.15625, 0.97119140625, 344.862890625,# 膝盖并拢过紧
# ]

#调整头部正直，平衡髋部坐姿哦！

# JSON_KEYPOINTS = [
#     1120.8515625, 0.986328125, 600.84375,    # 头部低头（y远大于理想，接近胸部）
#     1807.578125, 0.94384765625, 580.59375,   # 颈部前倾过度
#     1038.515625, 0.9638671875, 605.46875,    # 颈部前倾过度#
#     9110.7421875, 0.63916015625, 570.75,      # 面部贴近胸部
#     8112.8515625, 0.84033203125, 610.4375,   # 面部贴近胸部#
#     7137.4609375, 0.994140625, 476.953125,   # 肩膀耸起#
#     9140.625, 0.99560546875, 529.21875,      # 肩膀耸起
#     6169.6875, 0.97509765625, 476.71875,     # 左肘弯曲过度
#     8177.421875, 0.986328125, 524.53125,     # 右肘弯曲过度
#     4186.09375, 0.96630859375, 502.03125,    # 左手悬空
#     9192.1875, 0.98095703125, 518.90625,     # 右手悬空
#     7190.78125, 0.9970703125, 488.4375,      # 腰部弯曲
#     3193.125, 0.99755859375, 539.0625,       # 腰部弯曲
#     5209.0625, 0.9931640625, 491.25,         # 髋部前倾
#     9210.234375, 0.994140625, 540.0,         # 髋部前倾
#     7273.75, 0.9697265625, 489.375,          # 膝盖并拢过紧
#     6275.15625, 0.97119140625, 344.862890625,# 膝盖并拢过紧
# ]


IDEAL_POSTURE_KEYPOINTS_FLAT = [
    120.8515625,0.986328125,504.84375,
    107.578125,0.94384765625,493.59375,
    108.515625,0.9638671875,510.46875,
    110.7421875,0.63916015625,483.75,
    112.8515625,0.84033203125,518.4375,
    137.4609375,0.994140625,476.953125,
    140.625,0.99560546875,529.21875,
    169.6875,0.97509765625,476.71875,
    177.421875,0.986328125,524.53125,
    186.09375,0.96630859375,502.03125,
    192.1875,0.98095703125,518.90625,
    190.78125,0.9970703125,488.4375,
    193.125,0.99755859375,539.0625,
    209.0625,0.9931640625,491.25,
    210.234375,0.994140625,540.0,
    273.75,0.9697265625,489.375,
    275.15625,0.97119140625,344.862890625,
]

# ========== 工具函数 ==========
def parse_flat_keypoints(flat_list, min_conf=0.5):
    keypoints = []
    for i in range(0, len(flat_list), 3):
        # 添加数据校验和归一化处理
        x = flat_list[i] if flat_list[i] < 1000 else flat_list[i] / 10
        y = flat_list[i+1] if flat_list[i+1] < 1000 else flat_list[i+1] / 10
        conf = flat_list[i+2]
        
        if conf >= min_conf:
            keypoints.append((x, y))
        else:
            keypoints.append((None, None))
    return keypoints

def compute_angles(points):
    def angle(a, b, c):
        if a == (None, None) or b == (None, None) or c == (None, None):
            return None
            
        # 添加坐标范围校验
        ax, ay = a
        bx, by = b
        cx, cy = c
    
        ab = [a[0] - b[0], a[1] - b[1]]
        cb = [c[0] - b[0], c[1] - b[1]]
        dot = ab[0]*cb[0] + ab[1]*cb[1]
        mag_ab = math.hypot(*ab)
        mag_cb = math.hypot(*cb)
        if mag_ab == 0 or mag_cb == 0:
            return None
        cos_angle = max(min(dot / (mag_ab * mag_cb), 1.0), -1.0)
        return round(math.degrees(math.acos(cos_angle)), 2)

    left_body_angle = angle(points[5], points[11], points[13])
    right_body_angle = angle(points[6], points[12], points[14])
    
    # 计算平均身体角度
    if left_body_angle is not None and right_body_angle is not None:
        avg_body_angle = (left_body_angle + right_body_angle) / 2
    elif left_body_angle is not None:
        avg_body_angle = left_body_angle
    elif right_body_angle is not None:
        avg_body_angle = right_body_angle
    else:
        avg_body_angle = None

    return {
        "neck": angle(points[0], points[1], points[2]),
        "left_body": left_body_angle,
        "right_body": right_body_angle,
        "avg_body": avg_body_angle
    }

def get_access_token(api_key, secret_key):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    response = requests.post(url, params=params, proxies={"http": None, "https": None})
    token = response.json().get("access_token")
    print(f"获取令牌响应: {response.json()}")
    return token

def generate_posture_advice(token, posture_status, angles, user_prompt=None):
    if token is None:
        return "未能连接到AI服务，请检查您的姿势。"

    llm_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-turbo-128k?access_token={token}"

    if user_prompt is None:
        user_prompt = (
            f"你是一位关心办公人员健康和学生的虚拟助手，语气温和且友好，请根据以下姿势数据，给出20字实用的建议：\n"
            f"姿势状态：{posture_status}\n"
            f"颈部角度：{angles.get('neck', '--')}度\n"
            f"左侧身体角度：{angles.get('left_body', '--')}度\n"
            f"右侧身体角度：{angles.get('right_body', '--')}度\n"
            f"平均身体角度：{angles.get('avg_body', '--')}度\n"
        )

    print(f"发送给LLM的提示: {user_prompt}")

    payload = json.dumps({
        "messages": [{"role": "user", "content": user_prompt}],
        "penalty_score": 1,
        "enable_system_memory": False,
        "disable_search": True,
        "enable_citation": False,
        "enable_trace": False
    }, ensure_ascii=False)

    headers = {'Content-Type': 'application/json'}
    response = requests.post(llm_url, headers=headers, data=payload.encode("utf-8"), proxies={"http": None, "https": None})

    try:
        result = response.json()
        print("文心一言响应:", result)
        return result.get("result", "建议生成失败，请保持良好坐姿。")
    except Exception as e:
        print("解析响应失败:", e)
        return "系统错误，建议生成失败。"
def get_posture_report(token, angles, posture_status, current_points):
    # 详细的姿势问题分析
    issues = []
    
    # 头部位置分析
    if current_points[0][0] > current_points[1][0] * 1.2:
        issues.append("头部明显向右倾斜")
    elif current_points[0][0] < current_points[1][0] * 0.8:
        issues.append("头部明显向左倾斜")
    
    # 肩膀平衡分析
    shoulder_diff = abs(current_points[5][1] - current_points[6][1])
    if shoulder_diff > 20:
        issues.append(f"肩膀不平衡（差异：{shoulder_diff:.1f}像素）")
    
    # 坐姿分析
    hip_diff = abs(current_points[11][0] - current_points[12][0])
    if hip_diff > 30:
        issues.append(f"髋部不平衡（差异：{hip_diff:.1f}像素）")
    
    # 生成更精准的提示
    analysis = "检测到以下问题：" + "，".join(issues) if issues else "未检测到明显问题"
    
    # 构建更明确的用户提示
    user_prompt = (
        f"你是一位关心办公人员健康和学生的虚拟助手，友好的语气且个性化，请针对以下坐姿问题，给出20字实用的建议：\n"
        f"主要问题：{analysis}\n"
        f"详细分析：头部位置偏差较大，肩膀不平衡，坐姿不正\n"
        f"建议需避开重复表述，可分别从「头部矫正动作」「肩膀放松技巧」「脊柱挺直要点」「桌椅搭配调整」「定时活动提醒」等维度轮换，每次侧重1个具体细节，语气友好且实用"
    )
    
    return generate_posture_advice(token, posture_status, angles, user_prompt)


@app.route('/')
def home():
    """重定向到建议页面"""
    return redirect('/advice')

@app.route('/advice')
def serve_advice():
    """服务建议页面"""
    return send_from_directory(app.static_folder, "advice.html")

@app.route("/get_advice", methods=["GET"])
def get_advice():
    """
    获取AI生成的姿势建议
    返回JSON格式的建议数据
    """
        # 添加数据校验
    if len(JSON_KEYPOINTS) < 51 or len(JSON_KEYPOINTS) % 3 != 0:
        return jsonify({
            "error": "无效的关键点数据格式",
            "advice": "请检查关键点数据输入"
        }), 400
        
    # 添加日志记录原始数据
    print(f"原始关键点数据: {JSON_KEYPOINTS[:6]}...")
    
    # 使用当前的关键点数据
    current_points = parse_flat_keypoints(JSON_KEYPOINTS)
    angles = compute_angles(current_points)
    
    # 姿势状态判断逻辑
    ideal_points = parse_flat_keypoints(IDEAL_POSTURE_KEYPOINTS_FLAT, min_conf=0.0)
    diffs = []
    for c, i in zip(current_points, ideal_points):
        if None in c or None in i:
            continue
        dx = c[0] - i[0]
        dy = c[1] - i[1]
        diffs.append((dx**2 + dy**2) ** 0.5)
    
    avg_diff = round(sum(diffs) / len(diffs), 4) if diffs else 0
    posture_status = "good" if avg_diff < 10 else "bad"
    
    # 获取访问令牌，需要替换为你的实际 API Key 和 Secret Key
    api_key = "2YcoX4HqbcA6pMEolmNknwTQ"
    secret_key = "3eeNrmrpVcKnBEes3MZrcQJeMxqfLhEH"
    token = get_access_token(api_key, secret_key)
    
    # 生成建议
    advice = get_posture_report(token, posture_status, angles, current_points)
    
    # ===== 新增：调用IP音箱播报建议 =====
    try:
        send_tts(advice, delay_seconds=0)  # 建议生成后立即播报
        print("建议已通过IP音箱播报")
    except Exception as e:
        print(f"IP音箱播报失败: {e}")  # 仅打印错误，不阻塞主流程
    
    # 返回JSON数据
    return jsonify({
        "advice": advice,
        "posture": posture_status,
        "angles": angles,
        "timestamp": time.time()
    })

# ========== 主程序 ==========
if __name__ == "__main__":
    # 启动Flask应用
    print("启动姿势建议服务...")
    print(f"访问 http://localhost:5000/advice 查看建议页面")
    
    # 创建静态文件夹（如果不存在）
    os.makedirs(os.path.join(app.static_folder, "audio"), exist_ok=True)
    
    # 运行Flask应用
    app.run(host="0.0.0.0", port=5000, debug=True)
    
# ========== 主流程 ==========
# if __name__ == "__main__":
#     current_points = parse_flat_keypoints(JSON_KEYPOINTS)
#     angles = compute_angles(current_points)

#     # 判断姿势状态（根据与理想坐姿的差异）
#     ideal_points = parse_flat_keypoints(IDEAL_POSTURE_KEYPOINTS_FLAT, min_conf=0.0)
#     diffs = []
#     for c, i in zip(current_points, ideal_points):
#         if None in c or None in i:
#             continue
#         dx = c[0] - i[0]
#         dy = c[1] - i[1]
#         diffs.append((dx**2 + dy**2) ** 0.5)
#     avg_diff = round(sum(diffs) / len(diffs), 4) if diffs else 0
#     print(f"\n关键点平均差异: {avg_diff}")

#     posture_status = "good" if avg_diff < 10 else "bad"
#     print(f"姿势状态判断：{posture_status}")

#     advice = get_posture_report(angles, posture_status, current_points)
#     print("\n✅ AI 姿势建议：", advice)
    
        
#     # ===== 新增的IP音箱调用 =====
#     try:
#         # 立即播放建议，不延迟
#         send_tts(advice, delay_seconds=0)
#         print("建议已通过IP音箱播报")
#     except Exception as e:
#         print(f"IP音箱播报失败: {e}")

# 仅保留这段主程序块
if __name__ == "__main__":
    print("启动姿势建议服务...")
    print(f"访问 http://localhost:5000/advice 查看建议页面")
    os.makedirs(os.path.join(app.static_folder, "audio"), exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)  # 启动Flask服务