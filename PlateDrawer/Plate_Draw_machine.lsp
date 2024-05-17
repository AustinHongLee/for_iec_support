(defun GetFullDWGPath ()
  ; �����e DWG ��󪺧�����|�ê�^
  (setq dwgPath (strcat (getvar "dwgprefix") (getvar "dwgname")))
  dwgPath
)

(defun radium_change_func (value mode)
  ; �N�����ഫ�����שαN�����ഫ������
  (cond 
    ((or (= mode "r") (= mode "R")) ; �ˬd mode �O�_�� "r" �� "R"
     (setq finish_value (* (/ pi 180.0) value))) ; �N�����ഫ������
    ((or (= mode "d") (= mode "D")) ; �ˬd mode �O�_�� "d" �� "D"
     (setq finish_value (* (/ 180.0 pi) value))) ; �N�����ഫ������
  )
  finish_value ; ��^�ഫ�᪺��
)

(defun GetPartOfString (fullstring partIndex splitLogic / splitString start pos)
  ; �ϥΤ��j�Ť��Φr�Ŧ�ê�^���w����
  (setq start 0)
  (setq splitString '())

  ; �`�����Φr�Ŧ�
  (while (setq pos (vl-string-search splitLogic fullstring start))
    (setq splitString (append splitString (list (substr fullstring (+ start 1) (- pos start)))))
    (setq start (+ pos (strlen splitLogic)))
  )
  
  ; �K�[�̫�@�ӳ���
  (setq splitString (append splitString (list (substr fullstring (+ start 1)))))

  ; �ˬd partIndex �O�_���ġ]�j�� 0 �B���W�L���Ϋ�C�����ס^
  (if (and (> partIndex 0) (<= partIndex (length splitString)))
    (nth (1- partIndex) splitString ; ���ޱq 1 �}�l�A�C��q 0 �}�l�A�ҥH�n�� 1
    )
    "N/A" ; �p�G���޵L�ġA��^ "N/A"
  )
)

(defun ReadLinesFromFile (filePath)
  ; Ū�����w��󪺩Ҧ���ê�^�@�ӦC��
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
  ; �O�s��e�� OSMODE �ȡA�ñN��]�m�� 0 �H�T�ΩҦ��������I
  (setq currentOSMODE (getvar "OSMODE"))
  (setvar "OSMODE" 0)
  
  ; ���ܥΤ��ܲĤ@�Ӥ����I
  (setq c1 (getpoint "\n��ܱz���Ĥ@�Ӥ����I: "))
  
  ; ��� DWG ��󪺧�����|
  (setq dwgPath (GetFullDWGPath))
  
  ; �c�� Product_PlateForm.txt ��󪺸��|
  (setq filePath (strcat (substr dwgPath 1 (- (strlen dwgPath) (strlen (vl-filename-base dwgPath)) 4)) "Product_PlateForm.txt"))
  
  ; Ū�� Product_PlateForm.txt ��󤤪��Ҧ���
  (setq lines (ReadLinesFromFile filePath))

  ; ��l�Ƥ����I initialX �M initialY �H���B�~�Z�� offset
  (setq initialX (car c1))
  (setq initialY (cadr c1))
  (setq offset 200) ; �B�~�Z��

  (setq previousWidth 0) ; �O�s�e�@�ӯx�Ϊ��e��

  (foreach testing lines
    ; ���Φr�Ŧ�H����~�x�Ϊ����שM�e��
    (setq lengthX (GetPartOfString testing 1 "x"))
    (setq lengthY (GetPartOfString testing 2 "x"))

    ; �p��~�x�Ϊ��b���M�b�e
    (setq halfLengthX (/ (atof lengthX) 2))
    (setq halfLengthY (/ (atof lengthY) 2))

    ; ���Φr�Ŧ�H������x�Ϊ����שM�e��
    (setq f1 (vl-string-subst "" "]" (GetPartOfString testing 2 "[")))
    (setq innerLengthX (GetPartOfString f1 1 "x"))
    (setq innerLengthY (GetPartOfString f1 2 "x"))

    ; �p�⤺�x�Ϊ��b���M�b�e
    (setq innerHalfLengthX (/ (atof innerLengthX) 2))
    (setq innerHalfLengthY (/ (atof innerLengthY) 2))

    ; �����B�~���ƾ�
    (setq extraData (GetPartOfString testing 2 "_"))
    (setq holesize (GetPartOfString extraData 1 "%"))
    (setq boltsize (GetPartOfString extraData 2 "%"))

    ; �p��s�������I
    (setq c1x (+ initialX previousWidth halfLengthX halfLengthX offset))
    (setq c1 (list c1x initialY))

    ; ��s�e�@�ӯx�Ϊ��e��
    (setq previousWidth (* 2 halfLengthX))

    ; �w�q���צC��
    (setq a1_list '(135 45 315 225))
    
    ; �ϥδ`���p�� p1 �� p4�]�~�x�Ρ^
    (setq points '())
    (foreach a1 a1_list
      (setq radian (radium_change_func a1 "R"))
      (setq l1 (sqrt (+ (* halfLengthX halfLengthX) (* halfLengthY halfLengthY))))
      (setq point (polar c1 radian l1))
      (setq points (append points (list point)))
    )

    ; ���o�~�x�Ϊ��|���I
    (setq p1 (nth 0 points))
    (setq p2 (nth 1 points))
    (setq p3 (nth 2 points))
    (setq p4 (nth 3 points))

    ; �ϥ� RECTANG �R�Oø�s�~�x��
    (command "RECTANG" p1 p3)

    ; �ϥδ`���p�� p5 �� p8�]���x�Ρ^
    (setq innerPoints '())
    (foreach a1 a1_list
      (setq radian (radium_change_func a1 "R"))
      (setq l1 (sqrt (+ (* innerHalfLengthX innerHalfLengthX) (* innerHalfLengthY innerHalfLengthY))))
      (setq point (polar c1 radian l1))
      (setq innerPoints (append innerPoints (list point)))
    )

    ; ���o���x�Ϊ��|���I
    (setq p5 (nth 0 innerPoints))
    (setq p6 (nth 1 innerPoints))
    (setq p7 (nth 2 innerPoints))
    (setq p8 (nth 3 innerPoints))


    ; �ϥδ`��ø�s������
    (setq lemporary_cir holesize) ; ���ժ��|
    (foreach point innerPoints
      (command "CIRCLE" point lemporary_cir)
    )
	; �D�X��r��m mtxt1 OK
	(setq mtxt1 (polar p2 (radium_change_func 0 "R") (/ l1 2) ))
    	(setq mtxt2 (polar mtxt1 (radium_change_func 315 "R") c1x))
    	; ��r��X
  (setq plate_size_name (strcat lengthX "x" lengthY))
  (setq plate_thickness_name "9")
  (setq plate_material "A36/ss400")
  (setq plate_boltsize boltsize)
  (setq plate_holesize holesize)
    (setq formattedString (strcat "Plate Size: " plate_size_name "\n\n"
                                "Plate Material: " plate_material "\n\n"
                                "Plate Bolt Size: " plate_boltsize))
    (command "mtext" mtxt1 "H" (/ innerHalfLengthX 5) mtxt2 formattedString "") 
    ; ��s��lX����
    (setq initialX c1x)
  )

  ; ��_���e�� OSMODE ��
  (setvar "OSMODE" currentOSMODE)

  (princ)
)
