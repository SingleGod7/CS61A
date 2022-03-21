(define (my-filter func lst)
  (if (eq? lst nil)
      nil
      (if (func (car lst))
          (cons (car lst) (my-filter func (cdr lst)))
          (my-filter func (cdr lst)))))

(define (interleave s1 s2)
  (if (eq? s1 nil)
      s2
      (if (eq? s2 nil)
          s1
          (cons (car s1)
                (cons (car s2) (interleave (cdr s1) (cdr s2)))))))

(define (accumulate merger start n term)
  (if (= n 0)
      start
      (accumulate merger
                  (merger start (term n))
                  (- n 1)
                  term)))

(define (no-repeats lst)
  (if (eq? lst nil)
      nil
      (cons (car lst)
            (no-repeats
             (my-filter (lambda (y) (not (= (car lst) y)))
                        (cdr lst))))))
