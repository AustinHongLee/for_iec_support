(defun GetFullDWGPath ()
  ; 獲取當前 DWG 文件的完整路徑並返回
  (setq dwgPath (strcat (getvar "dwgprefix") (getvar "dwgname")))
  dwgPath
)

(defun radium_change_func (value mode)
  ; 將角度轉換為弧度或將弧度轉換為角度
  (cond 
    ((or (= mode "r") (= mode "R")) ; 檢查 mode 是否為 "r" 或 "R"
     (setq finish_value (* (/ pi 180.0) value))) ; 將角度轉換為弧度
    ((or (= mode "d") (= mode "D")) ; 檢查 mode 是否為 "d" 或 "D"
     (setq finish_value (* (/ 180.0 pi) value))) ; 將弧度轉換為角度
  )
  finish_value ; 返回轉換後的值
)

(defun GetPartOfString (fullstring partIndex splitLogic / splitString start pos)
  ; 使用分隔符分割字符串並返回指定部分
  (setq start 0)
  (setq splitString '())

  ; 循環分割字符串
  (while (setq pos (vl-string-search splitLogic fullstring start))
    (setq splitString (append splitString (list (substr fullstring (+ start 1) (- pos start)))))
    (setq start (+ pos (strlen splitLogic)))
  )
  
  ; 添加最後一個部分
  (setq splitString (append splitString (list (substr fullstring (+ start 1)))))

  ; 檢查 partIndex 是否有效（大於 0 且不超過分割後列表的長度）
  (if (and (> partIndex 0) (<= partIndex (length splitString)))
    (nth (1- partIndex) splitString ; 索引從 1 開始，列表從 0 開始，所以要減 1
    )
    "N/A" ; 如果索引無效，返回 "N/A"
  )
)

(defun ReadLinesFromFile (filePath)
  ; 讀取指定文件的所有行並返回一個列表
  (setq lines '())
  (setq file (open filePath "r"))
  (if file
    (progn
      (while (setq line (read-line file))
        (setq lines (append lines (list line))))
      (close file)
    )
  )
  lines
)

(defun c:Main_Draw ()
  ; 保存當前的 OSMODE 值，並將其設置為 0 以禁用所有物件鎖點
  (setq currentOSMODE (getvar "OSMODE"))
  (setvar "OSMODE" 0)
  
  ; 提示用戶選擇第一個中心點
  (setq c1 (getpoint "\n選擇您的第一個中心點: "))
  
  ; 獲取 DWG 文件的完整路徑
  (setq dwgPath (GetFullDWGPath))
  
  ; 構建 Product_PlateForm.txt 文件的路徑
  (setq filePath (strcat (substr dwgPath 1 (- (strlen dwgPath) (strlen (vl-filename-base dwgPath)) 4)) "Product_PlateForm.txt"))
  
  ; 讀取 Product_PlateForm.txt 文件中的所有行
  (setq lines (ReadLinesFromFile filePath))

  ; 初始化中心點 initialX 和 initialY 以及額外距離 offset
  (setq initialX (car c1))
  (setq initialY (cadr c1))
  (setq offset 200) ; 額外距離

  (setq previousWidth 0) ; 保存前一個矩形的寬度

  (foreach testing lines
    ; 分割字符串以獲取外矩形的長度和寬度
    (setq lengthX (GetPartOfString testing 1 "x"))
    (setq lengthY (GetPartOfString testing 2 "x"))

    ; 計算外矩形的半長和半寬
    (setq halfLengthX (/ (atof lengthX) 2))
    (setq halfLengthY (/ (atof lengthY) 2))

    ; 分割字符串以獲取內矩形的長度和寬度
    (setq f1 (vl-string-subst "" "]" (GetPartOfString testing 2 "[")))
    (setq innerLengthX (GetPartOfString f1 1 "x"))
    (setq innerLengthY (GetPartOfString f1 2 "x"))

    ; 計算內矩形的半長和半寬
    (setq innerHalfLengthX (/ (atof innerLengthX) 2))
    (setq innerHalfLengthY (/ (atof innerLengthY) 2))

    ; 提取額外的數據
    (setq extraData (GetPartOfString testing 2 "_"))
    (setq holesize (GetPartOfString extraData 1 "%"))
    (setq boltsize (GetPartOfString extraData 2 "%"))

    ; 計算新的中心點
    (setq c1x (+ initialX previousWidth halfLengthX halfLengthX offset))
    (setq c1 (list c1x initialY))

    ; 更新前一個矩形的寬度
    (setq previousWidth (* 2 halfLengthX))

    ; 定義角度列表
    (setq a1_list '(135 45 315 225))
    
    ; 使用循環計算 p1 到 p4（外矩形）
    (setq points '())
    (foreach a1 a1_list
      (setq radian (radium_change_func a1 "R"))
      (setq l1 (sqrt (+ (* halfLengthX halfLengthX) (* halfLengthY halfLengthY))))
      (setq point (polar c1 radian l1))
      (setq points (append points (list point)))
    )

    ; 取得外矩形的四個點
    (setq p1 (nth 0 points))
    (setq p2 (nth 1 points))
    (setq p3 (nth 2 points))
    (setq p4 (nth 3 points))

    ; 使用 RECTANG 命令繪製外矩形
    (command "RECTANG" p1 p3)

    ; 使用循環計算 p5 到 p8（內矩形）
    (setq innerPoints '())
    (foreach a1 a1_list
      (setq radian (radium_change_func a1 "R"))
      (setq l1 (sqrt (+ (* innerHalfLengthX innerHalfLengthX) (* innerHalfLengthY innerHalfLengthY))))
      (setq point (polar c1 radian l1))
      (setq innerPoints (append innerPoints (list point)))
    )

    ; 取得內矩形的四個點
    (setq p5 (nth 0 innerPoints))
    (setq p6 (nth 1 innerPoints))
    (setq p7 (nth 2 innerPoints))
    (setq p8 (nth 3 innerPoints))


    ; 使用循環繪製內螺孔
    (setq lemporary_cir holesize) ; 螺孔直徑
    (foreach point innerPoints
      (command "CIRCLE" point lemporary_cir)
    )
	; 求出文字位置 mtxt1 OK
	(setq mtxt1 (polar p2 (radium_change_func 0 "R") (/ l1 2) ))
    	(setq mtxt2 (polar mtxt1 (radium_change_func 315 "R") c1x))
    	; 文字輸出
  (setq plate_size_name (strcat lengthX "x" lengthY))
  (setq plate_thickness_name "9")
  (setq plate_material "A36/ss400")
  (setq plate_boltsize boltsize)
  (setq plate_holesize holesize)
    (setq formattedString (strcat "Plate Size: " plate_size_name "\n\n"
                                "Plate Material: " plate_material "\n\n"
                                "Plate Bolt Size: " plate_boltsize))
    (command "mtext" mtxt1 "H" (/ innerHalfLengthX 5) mtxt2 formattedString "") 
    ; 更新初始X坐標
    (setq initialX c1x)
  )

  ; 恢復之前的 OSMODE 值
  (setvar "OSMODE" currentOSMODE)

  (princ)
)
