import random
import time
import threading
import tkinter as tk

# 1. 核心演算法實作
# 選擇排序法 (Selection Sort)
def selection_sort(arr, draw_func, timer_func):
    n = len(arr)
    start_time = time.time()  # 記錄演算法開始時間
    
    for i in range(n):
        s = i  # 假設目前未排序區的第一個元素是最小值 [cite: 60]
        for j in range(i + 1, n):
            if arr[j] < arr[s]:  # 往後尋找有沒有更小的數值 [cite: 60]
                s = j            # 更新最小值的索引 [cite: 254]
        arr[i], arr[s] = arr[s], arr[i]  # 將最小值與左邊的數字交換 [cite: 60, 255]
        
        # 即時更新畫面與計時器
        draw_func(arr, [i, s])                    # 高亮正在交換的兩個柱子
        timer_func(time.time() - start_time)       # 更新計時器顯示
        time.sleep(0.01)                           # 稍微延遲以便觀察動畫
        
    timer_func(time.time() - start_time, final=True)  # 排序完成，將時間標籤變為綠色

# 泡泡排序法 (Bubble Sort)
def bubble_sort(arr, draw_func, timer_func):
    n = len(arr)
    start_time = time.time()
    
    # 從最後一個欄位開始往前固定（把大數往後擠）[cite: 260]
    for i in range(n - 1, 0, -1):
        for j in range(0, i):
            if arr[j] > arr[j + 1]:  # 如果前者比後者大，就進行交換 [cite: 259]
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                
                # 即時更新畫面與計時器
                draw_func(arr, [j, j + 1])
                timer_func(time.time() - start_time)
                time.sleep(0.01)
                
    timer_func(time.time() - start_time, final=True)

# 快速排序法核心邏輯 (Quick Sort Logic) 
def quick_sort_logic(arr, start, end, draw_func, timer_func, start_time):
    if start >= end:
        return
        
    pivot_idx = start  # 嚴格遵循簡報：將陣列最開始的元素當成基準點 [cite: 597, 611]
    left = start       # 左指標 [cite: 636, 659]
    right = end        # 右指標 [cite: 636, 660]
    
    # 兩指標開始朝中間移動，直到相撞為止 [cite: 662, 846]
    while left < right:
        # 右指標先往左移動，直到碰到小於基準點者 [cite: 688, 767, 1001]
        while left < right and arr[right] >= arr[pivot_idx]:
            right -= 1
        # 左指標再往右移動，直到碰到大於基準點者 [cite: 715, 793, 1002]
        while left < right and arr[left] <= arr[pivot_idx]:
            left += 1
            
        # 如果兩指標還沒相撞，交換左指標和右指標內容 [cite: 662, 741, 819]
        if left < right:
            arr[left], arr[right] = arr[right], arr[left]
            draw_func(arr, [left, right])          # 畫面上高亮這兩個交換的柱子
            timer_func(time.time() - start_time)   # 更新時間
            time.sleep(0.02)                       # 動畫延遲（此處會被遞迴多次放大）
            
    # 指標相撞，交換基準點與相撞位置（right）的數值 [cite: 846, 872, 1004]
    arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
    draw_func(arr, [pivot_idx, right])
    timer_func(time.time() - start_time)
    time.sleep(0.02)
    
    # 遞迴處理左邊與右邊的子陣列 [cite: 594, 605, 1005, 1006]
    quick_sort_logic(arr, start, right - 1, draw_func, timer_func, start_time)
    quick_sort_logic(arr, right + 1, end, draw_func, timer_func, start_time)

# 快速排序法包裝器（用來正確紀錄總時間與觸發完成狀態）
def quick_sort_wrapper(arr, draw_func, timer_func):
    start_time = time.time()
    quick_sort_logic(arr, 0, len(arr) - 1, draw_func, timer_func, start_time)
    timer_func(time.time() - start_time, final=True)  # 跑完時將計時器標籤轉為綠色


# 2. 視覺化 GUI 介面與 Thread 整合

class VividVisualizer:
    def __init__(self, root, num_elements=50):
        self.root = root
        self.root.title("Sorting Efficiency Comparison (Live Timer)")
        self.num_elements = num_elements
        self.reset_data()  # 初始化產生隨機亂序數列
        self.setup_gui()   # 建構介面

    # 產生 N 個隨機不重複的數字，並複製三份給不同的演算法獨立使用
    def reset_data(self):
        self.base_data = list(range(10, 10 + self.num_elements * 5, 5))
        random.shuffle(self.base_data)  # 隨機洗牌
        self.data_bubble = self.base_data.copy()
        self.data_select = self.base_data.copy()
        self.data_quick = self.base_data.copy()

    # 設定 Tkinter 視窗排版
    def setup_gui(self):
        # 控制按鈕區域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        self.btn = tk.Button(btn_frame, text="Start Sorting Simulations", command=self.start, font=("Arial", 12, "bold"))
        self.btn.pack()

        # 三個演算法的圖表顯示區域
        display_frame = tk.Frame(self.root)
        display_frame.pack(padx=10, pady=5)

        self.canvases = {}
        self.labels = {}
        algos = [("Bubble Sort", "bubble"), ("Selection Sort", "select"), ("Quick Sort", "quick")]
        
        # 動態產生三個並排的畫布與時間標籤
        for i, (name, key) in enumerate(algos):
            f = tk.Frame(display_frame, relief=tk.RIDGE, bd=2)
            f.grid(row=0, column=i, padx=5)
            tk.Label(f, text=name, font=("Arial", 11, "bold")).pack()
            
            # 建立黑色背景畫布
            c = tk.Canvas(f, width=300, height=250, bg="black")
            c.pack()
            
            # 建立紅色計時器標籤
            l = tk.Label(f, text="Time: 0.0000 s", font=("Courier", 12), fg="red")
            l.pack(pady=5)
            
            self.canvases[key] = c
            self.labels[key] = l

        self.draw_all()  # 畫出初始的未排序長條圖

    # 繪製所有畫布的現況
    def draw_all(self):
        self.draw_bars(self.canvases["bubble"], self.data_bubble)
        self.draw_bars(self.canvases["select"], self.data_select)
        self.draw_bars(self.canvases["quick"], self.data_quick)

    # 負責將陣列數值畫成長條圖的函式
    def draw_bars(self, canvas, data, highlights=[]):
        canvas.delete("all")  # 清空畫布
        if not data: return
        w = 300 / len(data)   # 計算每根柱子的寬度
        max_h = max(self.base_data)
        
        for i, v in enumerate(data):
            x0, x1 = i * w, (i + 1) * w
            y0 = 250 - (v / max_h * 220)  # 依數值比例計算高度
            
            # 如果是正在交換的元素，顯示為黃色，其餘為青藍色
            color = "yellow" if i in highlights else "cyan"
            canvas.create_rectangle(x0, y0, x1, 250, fill=color, outline="black")

    # 封裝執行緒安全的介面更新回傳函式 (Tkinter 規定必須回到主執行緒 root.after 更新 UI)
    def make_callbacks(self, key):
        canvas = self.canvases[key]
        label = self.labels[key]
        
        def d(arr, h=[]): 
            self.root.after(0, self.draw_bars, canvas, arr.copy(), h)
            
        def t(s, final=False): 
            color = "green" if final else "red"  # 執行中為紅，完成為綠
            self.root.after(0, lambda: label.config(text=f"Time: {s:.4f} s", fg=color))
            
        return d, t

    # 觸發開始按鈕
    def start(self):
        self.btn.config(state=tk.DISABLED)  # 鎖定按鈕避免重複點擊
        self.reset_data()                   # 重設一組新的亂數數據
        self.draw_all()                     # 畫出新的初始畫面
        
        # 取得各自的 UI 更新 Callback 函式
        d1, t1 = self.make_callbacks("bubble")
        d2, t2 = self.make_callbacks("select")
        d3, t3 = self.make_callbacks("quick")
        
        # 創建 3 個獨立的 Thread 同時跑排序，達成同步視覺化效能比較 (Hint 要求的 Thread 技術)
        threading.Thread(target=bubble_sort, args=(self.data_bubble, d1, t1)).start()
        threading.Thread(target=selection_sort, args=(self.data_select, d2, t2)).start()
        threading.Thread(target=quick_sort_wrapper, args=(self.data_quick, d3, t3)).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = VividVisualizer(root)
    root.mainloop()