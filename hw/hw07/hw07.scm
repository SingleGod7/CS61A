(define (cddr s) (cdr (cdr s)))

(define (cadr s) (car (cdr s)))

(define (caddr s) (car (cdr (cdr s))))

(define (ordered? s)
  (if (null? (cdr s))
      #t
      (if (> (car s) (car (cdr s)))
          #f
          (ordered? (cdr s)))))

(define (square x) (* x x))

(define (pow base exp)
  (if (= exp 1)
      base
      (if (= (modulo exp 2) 0)
          (pow (* base base) (/ exp 2))
          (* base (pow base (- exp 1))))))
