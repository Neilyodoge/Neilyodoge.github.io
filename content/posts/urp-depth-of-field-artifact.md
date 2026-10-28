---
title: URP景深的问题
date: '2022-07-11'
category: 技术分享
tags:
- URP
- 后处理
summary: URP 高斯景深在焦点位置出现黑线时的定位与调整记录。
cover: /media/legacy-urp-depth-01.png
source_id: urp-depth-of-field-artifact
legacy_url: https://neilyodoge.github.io/2022/07/11/urp-zi-dai-hou-chu-li-gao-si-jing-shen-de-artifact/
---

## 出现的问题

URP自带景深在高斯模糊的模式下，当End小于一定数值时会在焦点位置出现一条明显的黑线。

![URP 景深问题配图 1](/media/legacy-urp-depth-01.png)

![URP 景深问题配图 2](/media/legacy-urp-depth-02.png)

## 解决方案

黑线部分解决方案可以直接关掉End

![URP 景深问题配图 3](/media/legacy-urp-depth-03.png)

或者可以考虑通过shader调整

找到 GaussianDepthOfField.shader 文件 （在Packages-Universal RP-Shader-PostProcessing中）

在 FragCoC 中**限制FarEnd的最小值**，我这边选择的是 + 10，具体可以看情况微调

![URP 景深问题配图 4](/media/legacy-urp-depth-04.png)

![URP 景深问题配图 5](/media/legacy-urp-depth-05.png)

在 blur 中**增加采样偏移量**，这个值是直接从下面复制上来的，值再大一点的话某些焦点位置会在另外一个方向出现artifact所以选择了一个很小的数值 1e-4

![URP 景深问题配图 6](/media/legacy-urp-depth-06.png)

![URP 景深问题配图 7](/media/legacy-urp-depth-07.png)

在只修改采样偏移量不限制End数值范围的话，在某些焦点位置也还是会出现黑线的（如下图）

![URP 景深问题配图 8](/media/legacy-urp-depth-08.png)

## 原因

原因分为两部分

黑线部分是模糊空间的范围太小导致的，既下图中FS到FE的距离过小

![URP 景深问题配图 9](/media/legacy-urp-depth-09.png)

另一部分是物体边缘的artifact，这个是由于模糊的RT采样范围导致的

![URP 景深问题配图 10](/media/legacy-urp-depth-10.png)
