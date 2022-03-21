(define (over-or-under num1 num2)
  (cond 
    ((< num1 num2) -1)
    ((= num1 num2) 0)
    ((> num1 num2) 1)))

(define (make-adder num) (lambda (x) (+ x num)))

(define (composed f g) (lambda (x) (f (g x))))

(define a '(1))

(define c (list 3 4))

(define lst (list a 2 c 5))

(define (rm x) (lambda (y) (not (= y x))))
(define (remove item lst) (filter (rm item) lst))
