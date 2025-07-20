#!/bin/bash
for i in {1..10}
do
  curl -s -X POST http://192.168.31.94:8000/judge \
    -F "comment_text=这是微辣?第二天菊花冒火" \
    -F "comment_img=@D:\\extra-codes\\meituan_judge\\test\\test-pic.jpg" \
    -F "reply_img=@D:\\extra-codes\\meituan_judge\\test\\test-pic.jpg" \
    -F "reply_text=顾客评价说，第二天菊花上火。。餐品和菊花有什么关系，菊花怎么会上火??顾客完全没有基本知识，菊花属于植物类。。纯属虚假评论" \
    -F "related_text=招牌鸡肉炒米粉（1人份+微辣）" &
done
wait