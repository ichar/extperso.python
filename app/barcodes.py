# -*- coding: utf-8 -*-
# Copyright (c) 2010 Erik Karulf (erik@karulf.com)
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE

import sys

#from PIL import Image
#from PIL import ImageDraw

Image = ImageDraw = None

default_dos      = 'cp866'
default_unicode  = 'utf-8'
default_windows  = 'cp1251'
default_original = 'cp1252'

# Copied from http://en.wikipedia.org/wiki/Code_128
# Value Weights 128A    128B    128C
CODE128_CHART = """
0       212222  space   space   00
1       222122  !       !       01
2       222221  "       "       02
3       121223  #       #       03
4       121322  $       $       04
5       131222  %       %       05
6       122213  &       &       06
7       122312  '       '       07
8       132212  (       (       08
9       221213  )       )       09
10      221312  *       *       10
11      231212  +       +       11
12      112232  ,       ,       12
13      122132  -       -       13
14      122231  .       .       14
15      113222  /       /       15
16      123122  0       0       16
17      123221  1       1       17
18      223211  2       2       18
19      221132  3       3       19
20      221231  4       4       20
21      213212  5       5       21
22      223112  6       6       22
23      312131  7       7       23
24      311222  8       8       24
25      321122  9       9       25
26      321221  :       :       26
27      312212  ;       ;       27
28      322112  <       <       28
29      322211  =       =       29
30      212123  >       >       30
31      212321  ?       ?       31
32      232121  @       @       32
33      111323  A       A       33
34      131123  B       B       34
35      131321  C       C       35
36      112313  D       D       36
37      132113  E       E       37
38      132311  F       F       38
39      211313  G       G       39
40      231113  H       H       40
41      231311  I       I       41
42      112133  J       J       42
43      112331  K       K       43
44      132131  L       L       44
45      113123  M       M       45
46      113321  N       N       46
47      133121  O       O       47
48      313121  P       P       48
49      211331  Q       Q       49
50      231131  R       R       50
51      213113  S       S       51
52      213311  T       T       52
53      213131  U       U       53
54      311123  V       V       54
55      311321  W       W       55
56      331121  X       X       56
57      312113  Y       Y       57
58      312311  Z       Z       58
59      332111  [       [       59
60      314111  \       \       60
61      221411  ]       ]       61
62      431111  ^       ^       62
63      111224  _       _       63
64      111422  NUL     `       64
65      121124  SOH     a       65
66      121421  STX     b       66
67      141122  ETX     c       67
68      141221  EOT     d       68
69      112214  ENQ     e       69
70      112412  ACK     f       70
71      122114  BEL     g       71
72      122411  BS      h       72
73      142112  HT      i       73
74      142211  LF      j       74
75      241211  VT      k       75
76      221114  FF      l       76
77      413111  CR      m       77
78      241112  SO      n       78
79      134111  SI      o       79
80      111242  DLE     p       80
81      121142  DC1     q       81
82      121241  DC2     r       82
83      114212  DC3     s       83
84      124112  DC4     t       84
85      124211  NAK     u       85
86      411212  SYN     v       86
87      421112  ETB     w       87
88      421211  CAN     x       88
89      212141  EM      y       89
90      214121  SUB     z       90
91      412121  ESC     {       91
92      111143  FS      |       92
93      111341  GS      }       93
94      131141  RS      ~       94
95      114113  US      DEL     95
96      114311  FNC3    FNC3    96
97      411113  FNC2    FNC2    97
98      411311  ShiftB  ShiftA  98
99      113141  CodeC   CodeC   99
100     114131  CodeB   FNC4    CodeB
101     311141  FNC4    CodeA   CodeA
102     411131  FNC1    FNC1    FNC1
103     211412  StartA  StartA  StartA
104     211214  StartB  StartB  StartB
105     211232  StartC  StartC  StartC
106     2331112 Stop    Stop    Stop
"""


class Code128Barcode:
    """
        Code 128 Barcode Generator.
        Image and IDAutomation fonts implemented.

        Code sets A,B,C.
        Despite its name, Code 128 does not have 128 distinct symbols, so it cannot represent 128 code points directly. 
        To represent all 128 ASCII values, it shifts among three code sets (A, B, C). Together, code sets A and B cover all 128 
        ASCII characters. Code set C is used to efficiently encode digit strings. The initial subset is selected by using the 
        appropriate start symbol. Within each code set, some of the 103 data code points are reserved for shifting to one of the 
        other two code sets. The shifts are done using code points 98 and 99 in code sets A and B, 100 in code sets A and C and 101 
        in code sets B and C to switch between them):

        128A (Code Set A) – ASCII characters 00 to 95 (0–9, A–Z and control codes), special characters, and FNC 1–4
        128B (Code Set B) – ASCII characters 32 to 127 (0–9, A–Z, a–z), special characters, and FNC 1–4
        128C (Code Set C) – 00–99 (encodes two digits with a single code point) and FNC1
        
        https://en.wikipedia.org/wiki/Code_128
    """

    def __init__(self):
        code128 = CODE128_CHART.split()

        self.values = [int(value) for value in code128[0::5]]
        self.weights = dict(zip(self.values, code128[1::5]))
        self.code128a = dict(zip(code128[2::5], self.values))
        self.code128b = dict(zip(code128[3::5], self.values))
        self.code128c = dict(zip(code128[4::5], self.values))

        for charset in (self.code128a, self.code128b):
            charset[' '] = charset.pop('space')

    def code128_format(self, data):
        """
            Generate an optimal barcode from ASCII text
        """
        text = str(data)
        pos = 0
        length = len(text)
        
        # Start Code
        if text[:2].isdigit() and length > 1:
            charset = self.code128c
            codes = [charset['StartC']]
        else:
            charset = self.code128b
            codes = [charset['StartB']]

        # Data
        while pos < length:
            if charset is self.code128c:
                if text[pos:pos+2].isdigit() and length - pos > 1:
                    # Encode Code C two characters at a time
                    codes.append(int(text[pos:pos+2]))
                    pos += 2
                else:
                    # Switch to Code B
                    codes.append(charset['CodeB'])
                    charset = self.code128b
            elif text[pos:pos+4].isdigit() and length - pos >= 4:
                # Switch to Code C
                codes.append(charset['CodeC'])
                charset = self.code128c
            else:
                # Encode Code B one character at a time
                codes.append(charset[text[pos]])
                pos += 1

        # Checksum
        checksum = 0
        for weight, code in enumerate(codes):
            checksum += max(weight, 1) * code
        x = checksum % 103
        codes.append(x)

        # Stop Code
        codes.append(charset['Stop'])
        return codes

    def code128_image(self, data, height=100, thickness=3, quiet_zone=True):
        """
            Generate barcode image
        """
        if Image is None:
            return None

        if not data[-1] == self.code128b['Stop']:
            data = self.code128_format(data)

        barcode_widths = []
        for code in data:
            for weight in self.weights[code]:
                barcode_widths.append(int(weight) * thickness)
        width = sum(barcode_widths)
        x = 0

        if quiet_zone:
            width += 20 * thickness
            x = 10 * thickness

        # Monochrome Image
        img = Image.new('1', (width, height), 1)
        draw = ImageDraw.Draw(img)
        draw_bar = True

        for width in barcode_widths:
            if draw_bar:
                draw.rectangle(((x, 0), (x + width - 1, height)), fill=0)
            draw_bar = not draw_bar
            x += width

        return img

    def ttf(self, value, encoding=default_windows):
        """
            IDAutomation.com fonts encodings
        """
        s = ''.join([chr(x == 0 and 194 or x > 98 and x+100 or x+32) for x in self.code128_format(value)])
        if encoding:
            try:
                return s.encode(default_original).decode(encoding)
            except:
                pass
        return s


class I25Barcode:

    def ttf(self, value, encoding=default_windows):
        tmp = ''
        for s in value:
            if s.isdigit():
                tmp += s
        if len(tmp) % 2 == 1:
            tmp = '0' + tmp
        res = ''
        for n in range(0, len(tmp), 2):
            x = int(tmp[n:n+2])
            if x <= 93:
                res += chr(x+33)
            else:
                res += chr(x+103)
        s = '%s%s%s' % (chr(203), res, chr(204))
        if encoding:
            return s.encode(default_original).decode(encoding)
        return s

EAN13_CODE = {
    '0' : (0,0,0,0,0,0,0),
    '1' : (0,0,0,1,0,1,1),
    '2' : (0,0,0,1,1,0,1),
    '3' : (0,0,0,1,1,1,0),
    '4' : (0,0,1,0,0,1,1),
    '5' : (0,0,1,1,0,0,1),
    '6' : (0,0,1,1,1,0,0),
    '7' : (0,0,1,0,1,0,1),
    '8' : (0,0,1,0,1,1,0),
    '9' : (0,0,1,1,0,1,0),
}


class EAN13Barcode:
    
    def ttf(self, value, encoding=default_windows):
        res = ''
        if not value or len(value) != 13:
            return res
        c = '0'
        for n, s in enumerate(value):
            if n == 0:
                res = '%s(' % chr(ord(s)+37)
                c = s
            elif n < 7:
                res += chr(ord(s) + 17 * EAN13_CODE[c][n])
            else:
                res += chr(ord(s) + 27)
            if n == 6:
                res += '*'
        res += '('
        return res


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) < 2 or argv[1].lower() in ('/h', '/help', '-h', 'help', '--help'):
        pass
    else:
        value = argv[1]
        assert value, "Barcode value should be present as the first argument."
        
        barcode = Code128Barcode() # 5160015910802
        
        print(barcode.code128_format(value))
        print(barcode.ttf(value))
        
        barcode = EAN13Barcode()
        
        print(barcode.ttf(value))
