# BitcoinAutoTrade
## 2021 씨애랑 소프트웨어 전시회
Python의 Upbit API를 활용한 가상화폐 자동거래 프로그램입니다.

단기투자 기법 중 전고점 돌파 매매 전략을 참고하여 만들었습니다. <br>
(참고 : https://epthffh.tistory.com/entry/%EB%8F%8C%ED%8C%8C-%EB%A7%A4%EB%A7%A4-%EC%A2%85%EB%A5%98)

암호화폐의 가격이 전 고점을 넘어서고, 다시 하락한 후 조정기간에 인공지능이 암호화폐의 가격이 오를 것으로 예상하면 매수하고 가격이 같거나 줄어들 것으로 예상하면 매수를 하지 않게끔 코드를 만들었습니다. 

인공지능 모델은 Facebook의 Prophet을 사용했습니다.<br>
(참고:https://facebook.github.io/prophet/)

시연영상은 issues에 있습니다. 아쉽게도 전 고점을 돌파하고 조정기간에 매수하는 동작을 녹화하지는 못했으나 Upbit API를 통해 암호화폐의 가격,200분 동안의 최고가,현재 사용자의 잔고를 불러오는 기능은 작 잘동합니다.
