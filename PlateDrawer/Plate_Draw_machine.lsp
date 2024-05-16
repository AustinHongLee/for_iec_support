(defun GetFullDWGPath ()
  (setq dwgPath (strcat (getvar "dwgprefix") (getvar "dwgname")))
  ; dwgPath = direction for this dwg path 

)

(defun radium_change_func (value mode)
  ; we need to know what kind of value input here 
  (cond 
    ((or (= mode "r") (= mode "R")) ; 檢查 mode 是否為 "r" 或 "R"
     (setq finish_value (* (/ pi 180.0) value))) ; 將角度轉換為弧度
    ((or (= mode "d") (= mode "D")) ; 檢查 mode 是否為 "d" 或 "D"
     (setq finish_value (* (/ 180.0 pi) value))) ; 將弧度轉換為角度
  )
  finish_value ; 返回轉換後的值
)

(defun GetPartOfString (fullstring partIndex / splitString splitLogic)
  (setq splitLogic (if splitLogic splitLogic "-")) ; 預設分隔符為 "-"，如果沒有提供則使用 "-"
  
  ; 使用 VL 串操作函數分割字符串
  (setq splitString (vl-string->list (vl-string-subst " " splitLogic fullstring)))
  
  ; 檢查 partIndex 是否有效（大於 0 且不超過分割後列表的長度）
  (if (and (> partIndex 0) (<= partIndex (length splitString)))
    (nth (1- partIndex) splitString) ; 索引從 1 開始，列表從 0 開始，所以要減 1
    "N/A" ; 如果索引無效，返回 "N/A"
  )
)



(defun c:Main_Draw ()
  (setq c1 (getpoint "\nChoice your first point \t attention: this is rec center point !!"))
  
  ; 測試字符串
  (setq testing "290x290x9[220x220]")
  
  ; 分割字符串
  (setq t1 (GetPartOfString testing 1 "x"))
  (setq t2 (GetPartOfString testing 2 "x"))
  (setq t3 (GetPartOfString testing 3 "x"))
  
  ; 替換字符串中的 "]"
  (setq f1 (vl-string-subst "" "]" (GetPartOfString testing 2 "[")))
  
  ; 分割子字符串
  (setq t4 (GetPartOfString f1 1 "x"))
  (setq t5 (GetPartOfString f1 2 "x"))
  
  (setq p1 ( polar c1 (radium_change_func(135 "R") (sqrt(int(t1))))))

)
