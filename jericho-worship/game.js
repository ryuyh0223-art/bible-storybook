
const ART={"road":"assets/road.webp","inn":"assets/inn.webp","city":"assets/city.webp","vista":"assets/vista.webp","priest":"assets/priest.webp","samaritan":"assets/samaritan.webp","merchant":"assets/merchant.webp","wounded":"assets/wounded.webp","priest_normal":"assets/priest_normal.webp","priest_happy":"assets/priest_happy.webp","priest_surprise":"assets/priest_surprise.webp","priest_worry":"assets/priest_worry.webp","priest_resolve":"assets/priest_resolve.webp","priest_intro":"assets/priest_intro.webp","priest_inn":"assets/priest_inn.webp","priest_win":"assets/priest_win.webp","priest_lose":"assets/priest_lose.webp","priest_care0":"assets/priest_care0.webp","priest_care1":"assets/priest_care1.webp","priest_last0":"assets/priest_last0.webp","priest_last1":"assets/priest_last1.webp","samaritan_normal":"assets/samaritan_normal.webp","samaritan_happy":"assets/samaritan_happy.webp","samaritan_surprise":"assets/samaritan_surprise.webp","samaritan_worry":"assets/samaritan_worry.webp","samaritan_resolve":"assets/samaritan_resolve.webp","samaritan_intro":"assets/samaritan_intro.webp","samaritan_inn":"assets/samaritan_inn.webp","samaritan_win":"assets/samaritan_win.webp","samaritan_lose":"assets/samaritan_lose.webp","samaritan_care0":"assets/samaritan_care0.webp","samaritan_care1":"assets/samaritan_care1.webp","samaritan_carry0":"assets/samaritan_carry0.webp","samaritan_carry1":"assets/samaritan_carry1.webp","samaritan_last0":"assets/samaritan_last0.webp","samaritan_last1":"assets/samaritan_last1.webp","merchant_normal":"assets/merchant_normal.webp","merchant_happy":"assets/merchant_happy.webp","merchant_surprise":"assets/merchant_surprise.webp","merchant_worry":"assets/merchant_worry.webp","merchant_resolve":"assets/merchant_resolve.webp","merchant_intro":"assets/merchant_intro.webp","merchant_inn":"assets/merchant_inn.webp","merchant_win":"assets/merchant_win.webp","merchant_lose":"assets/merchant_lose.webp","merchant_care0":"assets/merchant_care0.webp","merchant_care1":"assets/merchant_care1.webp","merchant_last0":"assets/merchant_last0.webp","merchant_last1":"assets/merchant_last1.webp","priest_turnback":"assets/priest_turnback.webp","samaritan_turnback":"assets/samaritan_turnback.webp","merchant_turnback":"assets/merchant_intro.webp","merchant_carry0_g0":"assets/merchant_carry0_g0.webp","priest_carry1_g0":"assets/priest_carry1_g0.webp","merchant_carry1_g0":"assets/merchant_carry1_g0.webp","priest_carry0_g0":"assets/priest_carry0_g0.webp","priest_carry0_g1":"assets/priest_carry0_g1.webp","merchant_carry0_g1":"assets/merchant_carry0_g1.webp","priest_carry1_g1":"assets/priest_carry1_g1.webp","merchant_carry1_g1":"assets/merchant_carry1_g1.webp","discovery":"assets/discovery.webp","reflection":"assets/reflection.webp"};
const R={
 priest:{name:'제사장',mini:'딸과 저녁 약속',mission:'해 지기 전에 집에 돌아가기',
   scenes:[
    {bg:'city',line:'성전에서 일을 마친 제사장이 여리고로 돌아가고 있었어.'},
    {bg:'city',speaker:'딸',line:'“아빠! 오늘은 꼭 일찍 오셔야 해요. 같이 저녁 먹기로 했잖아요!”',face:'priest_happy'},
    {bg:'road',speaker:'제사장',line:'“그럼! 오늘은 반드시 약속을 지켜야지.”',expr:'happy'}],
   meet:'“어? 저 사람이 왜 저기 쓰러져 있지?”',
   missionWin:[
    {bg:'city',line:'제사장은 해가 지기 전에 집에 도착했어.'},
    {bg:'city',speaker:'딸',line:'“아빠! 약속 지키셨네요!”',face:'priest_happy'},
    {bg:'city',line:'제사장은 딸과 마주 앉아 저녁을 먹었어.'}],
   give:[
    {label:'내 외투를 벗어 덮어준다.',but:'하지만 돌아가는 길에는 입을 외투가 없어.',loss:'외투',line:'제사장은 외투를 벗어 나그네에게 덮어주었어. 이제 어깨에는 가벼운 옷만 남았지.',item:'cloak'},
    {label:'내 물주머니와 천을 꺼낸다.',but:'하지만 남은 길에서 마실 물이 부족해.',loss:'물주머니의 물',line:'제사장은 물과 천을 꺼냈어. 나그네를 살피고 나니 물주머니가 거의 비어 있었어.',item:'water'}],
   move:[
    {label:'지나가는 짐꾼에게 은전을 주고 짐승을 빌린다.',but:'하지만 집에 돌아갈 때 쓸 돈이 줄어.',loss:'은전 한 닢',line:'제사장은 짐꾼에게 은전 한 닢을 주고 짐승을 빌렸어. 나그네를 등에 태우고 고삐를 잡았지.',item:'coin'},
    {label:'힘들어도 직접 부축해서 함께 간다.',but:'하지만 다친 사람을 받쳐주며 먼 길을 걸어야 해.',loss:'남은 기운',line:'제사장은 다친 사람을 천천히 일으켜 세웠어. 나그네의 팔을 자기 어깨에 걸치고 한 걸음씩 걸었지. 힘이 들었지만 끝까지 곁을 지켰어.',item:'effort'}],
   lose:[
    {bg:'city',line:'다음 날 이른 아침, 제사장은 집에 돌아왔어.'},
    {bg:'city',line:'딸은 아직 잠들어 있었어. 어제 함께 먹기로 했던 저녁은 놓치고 말았지.'}],
   parting:'“딸과의 약속은 못 지켰지만… 길에서 만난 사람도 그냥 두고 갈 수는 없었어.”'
 },
 samaritan:{name:'여행자',mini:'일행과 만나기',mission:'해 지기 전에 여행 일행과 합류하기',
   scenes:[
    {bg:'road',line:'사마리아에서 온 여행자가 나귀에 짐을 싣고 여리고로 향하고 있었어.'},
    {bg:'road',speaker:'동행인',line:'“해 지기 전에 여리고에 모입시다. 내일 아침에 같이 출발해야 하니까요!”',face:'samaritan_normal'},
    {bg:'road',speaker:'여행자',line:'“좋아! 나귀도 준비됐고, 짐도 빠진 게 없어. 늦지 말아야지.”',expr:'happy'}],
   meet:'“잠깐, 저 사람… 혼자서는 못 일어나겠는데?”',
   missionWin:[
    {bg:'city',line:'여행자는 약속한 시간에 여리고에 도착했어.'},
    {bg:'city',speaker:'동행인',line:'“잘 오셨소! 내일 아침 함께 떠납시다!”',face:'samaritan_happy'},
    {bg:'city',line:'여행자는 일행과 만나 다음 날 여행을 준비했어.'}],
   give:[
    {label:'기름과 포도주, 천을 사용한다.',but:'하지만 여행 중 쓰려고 챙긴 물건이 줄어.',loss:'기름·포도주와 천',line:'여행자는 기름과 포도주를 꺼내 상처를 돌보고, 천으로 감싸주었어.',item:'oil'},
    {label:'여행용 천과 물을 사용한다.',but:'하지만 남은 길에 마실 물이 부족해.',loss:'여행용 천과 물',line:'여행자는 물과 천으로 나그네를 살폈어. 이제 남은 길에 쓸 물이 별로 없어.',item:'water'}],
   move:[
    {label:'나귀의 짐을 내가 메고 나그네를 태운다.',but:'하지만 무거운 짐을 직접 지고 걸어야 해.',loss:'편하게 옮길 수 있던 짐',line:'여행자는 나그네를 나귀에 태우고, 짐보따리는 자기 등에 메었어. 짐이 묵직하게 느껴졌지.',item:'burden'},
    {label:'짐보따리 하나를 내려놓고 나그네를 태운다.',but:'하지만 그 보따리는 놓고 가야 해.',loss:'짐보따리 한 개',line:'여행자는 짐보따리 하나를 바위 옆에 남겨두고, 나그네를 나귀에 태웠어.',item:'bundle'}],
   lose:[
    {bg:'city',line:'다음 날 아침, 여행자가 여리고에 도착했을 땐 일행이 이미 떠난 뒤였어.'},
    {bg:'city',line:'함께 떠나려던 여행은 놓쳤지. 이제 계획을 새로 세워야 해.'}],
   parting:'“일행은 놓쳤지만… 오늘은 이 사람을 먼저 도와야 했어.”'
 },
 merchant:{name:'대추야자 상인',mini:'대추야자 납품',mission:'해 지기 전에 대추야자 세 광주리 팔기',
   scenes:[
    {bg:'city',line:'여리고 근처에 사는 상인이 대추야자 세 광주리를 수레에 실었어.'},
    {bg:'city',speaker:'구매자',line:'“해 지기 전에 세 광주리 모두 가져오시오. 난 오늘 떠나야 하오!”',face:'merchant_normal'},
    {bg:'road',speaker:'상인',line:'“좋았어! 오늘만 잘 팔면 가족에게 돈을 가져갈 수 있어!”',expr:'happy'}],
   meet:'“어? 사람이 쓰러져 있잖아! 무슨 일이지?”',
   missionWin:[
    {bg:'city',line:'상인은 대추야자 세 광주리를 약속한 시간에 가져갔어.'},
    {bg:'city',speaker:'구매자',line:'“세 광주리 맞군! 여기 약속한 돈이오.”',face:'merchant_happy'},
    {bg:'city',line:'상인은 돈주머니를 챙기며 활짝 웃었어. 오늘 장사는 성공이야!'}],
   give:[
    {label:'대추야자 포장천을 풀어 사용한다.',but:'하지만 광주리의 포장이 풀려버려.',loss:'광주리의 포장천',line:'상인은 광주리의 천을 풀어 나그네의 상처를 감싸줬어. 대추야자 한 광주리가 그대로 드러났지.',item:'cloth'},
    {label:'내 외투를 벗어 덮어준다.',but:'하지만 밤길에 입을 외투가 없어.',loss:'외투',line:'상인은 자기 외투를 벗어 나그네에게 덮어주었어. 외투를 벗으니 바람이 서늘하게 느껴졌어.',item:'cloak'}],
   move:[
    {label:'광주리 하나를 내려놓고 수레에 태운다.',but:'하지만 세 광주리를 모두 가져갈 수 없어.',loss:'대추야자 한 광주리',line:'상인은 광주리 하나를 길가에 남겨두고, 나그네를 수레에 태웠어. 수레에는 두 광주리만 남았지.',item:'basket'},
    {label:'짐꾼에게 은전을 주고 광주리를 맡긴다.',but:'하지만 가족에게 가져갈 돈이 줄어.',loss:'은전 한 닢',line:'상인은 은전을 주고 광주리 하나를 짐꾼에게 맡겼어. 두 광주리가 남은 수레에 나그네를 태웠지.',item:'coin'}],
   lose:[
    {bg:'city',line:'다음 날 아침, 상인이 장터에 도착했을 땐 구매자가 이미 떠난 뒤였어.'},
    {bg:'city',line:'수레에 남은 대추야자도 팔지 못했지. 오늘 거래는 실패야.'}],
   parting:'“오늘은 장사를 못 했네. 그래도 이 사람을 그냥 두고 올 수는 없었지.”'
 }
};
const common={
 intro:'예수님 시대의 길을 배경으로 한 선택형 이야기야. 오늘은 네가 직접 주인공이 되어봐!',
 wounded:'길가에 한 사람이 쓰러져 있어. 강도를 만났는지 짐도, 겉옷도 없어.',
 patient:'“으으… 누가 좀… 도와주세요…”',
 inn:'한참 뒤, 주막에 도착했어. 주막 주인이 나그네를 침상에 눕혀주었지.',
 keeper:'“방은 내어주겠소. 그런데 밤새 누가 이 사람을 챙기겠소?”'
};
let game={dayPhase:'day',missionExpired:false,clockScene:null,inventoryProgress:{give:null,carry:null,final:null,trade:null},role:null,route:null,returned:false,give:null,carry:null,final:null,step:0,queue:[],event:'',scene:'select'};
const $=id=>document.getElementById(id);
function queue(steps){game.queue=steps;game.step=0;render()}
function story(bg,line,speaker='',expr='',opts={}){return {type:'story',bg,line,speaker,expr,...opts}}
function quiz(title,options,callback,bg='road',opts={}){return {type:'quiz',bg,title,options,callback,...opts}}
function ending(title,subtitle,storyText){return {type:'ending',bg:'city',title,subtitle,storyText}}
function reflection(){return {type:'reflection',bg:'road',pic:'reflection'}}
function chooseRole(id){
 game={dayPhase:'day',missionExpired:false,clockScene:null,inventoryProgress:{give:null,carry:null,final:null,trade:null},role:id,route:null,returned:false,give:null,carry:null,final:null,step:0,queue:[],event:'',scene:'intro'};
 const r=R[id];const a=r.scenes.map(v=>story(v.bg,v.line,v.speaker||'',v.expr||'',{face:v.face,pic:id+'_intro'}));
 queue([
  ...a,
  story('road','구불구불한 광야길이 끝없이 이어졌어.', '', '',{pic:id+'_intro'}),
  story('road','“으으……”\n바위 뒤에서 작은 신음소리가 들려.', '', '',{wounded:true,pose:'surprise',pic:id+'_meet'}),
  story('road',common.wounded,'','',{wounded:true}),
  story('road',common.patient,'다친 사람','worry',{wounded:true,face:'wounded'}),
  story('road',r.meet,r.name,'worry',{wounded:true,pose:'worry',pic:id+'_meet'}),
  quiz('지금, 어떻게 할까?',[
   {label:'미션을 위해 여리고로 간다.',but:'하지만 다친 사람을 두고 가야 해.',tag:'mission'},
   {label:'멈춰서 다친 사람을 돕는다.',but:'하지만 오늘의 미션은 포기해야 해.',tag:'neighbor'}
  ],pickPath,'road',{wounded:true,pic:id+'_choice'})
 ]);
}
function pickPath(i){
 game.route=i===0?'mission':'neighbor';game.event='';
 if(i===0){
  const r=R[game.role];queue([
   story('road','주인공은 다시 길을 걸었어.\n아직은 약속한 시간에 도착할 수 있겠어.','', '',{pose:'walk',pic:game.role+'_intro'}),
   story('road','구불구불한 길을 한참 내려오니 갈림길이 보였어.\n저 멀리 여리고 성벽도 보이기 시작했지.','', '',{pic:game.role+'_turnback'}),
   story('road',r.name==='제사장'?'“조금만 더 가면 딸과의 약속을 지킬 수 있어.”':game.role==='samaritan'?'“일행이 떠나기 전에 도착할 수 있겠어.”':'“구매자가 떠나기 전에 대추야자를 팔 수 있겠어.”',r.name,'worry',{pic:game.role+'_turnback'}),
   quiz('이제 어느 길로 갈까?',[
    {label:'여리고까지 계속 간다.',but:'하지만 아까 만난 사람은 그대로 남아 있어.'},
    {label:'그 사람에게 돌아간다.',but:'하지만 오늘의 미션은 포기해야 해.'}
   ],pickAfterPass,'road',{pic:game.role+'_turnback'})
  ]);return}
 beginHelp(false);
}

function pickAfterPass(i){
 if(i===0){
  game.route='mission';
  const r=R[game.role];queue([
   story('road','주인공은 여리고를 향해 계속 걸었어.\n이제 조금만 더 가면 도착이야.','', '',{pic:game.role+'_turnback'}),
   ...r.missionWin.map(x=>story(x.bg,x.line,x.speaker||'',x.expr||'',{face:x.face,pic:game.role+'_win',inventoryApply:game.role==='merchant'?{stage:'trade',choice:0}:null})),
   ending('미션 성공!','하지만 좋은 이웃이 되진 못했어.',''), reflection()
  ]);return;
 }
 game.route='neighbor';game.returned=true;
 queue([
  story('road','주인공은 발길을 돌렸어.\n올라왔던 길을 다시 걷기 시작했지.','', '',{pic:game.role+'_turnback'}),
  story('road','바위 옆으로 돌아오니, 다친 사람은 그대로 누워 있었어.','', '',{wounded:true,pic:game.role+'_meet'}),
  story('road','“제가 왔어요. 지금부터 도와드릴게요!”',R[game.role].name,'resolve',{wounded:true,pic:game.role+'_meet'}),
  quiz('이 사람에게 뭘 해줄까?',R[game.role].give.map(x=>({label:x.label,but:x.but})),pickGive,'road',{wounded:true,close:true,pic:game.role+'_choice'})
 ]);
}
function beginHelp(returned){
 game.route='neighbor';game.returned=!!returned;
 const r=R[game.role];queue([
  story('road','“잠깐만요. 제가 도와드릴게요!”',r.name,'resolve',{wounded:true,pose:'resolve',pic:game.role+'_meet'}),
  story('road','오늘 약속은 지키기 어렵겠어.\n그래도 지금은 이 사람부터 도와야 해.','', '',{wounded:true,pic:game.role+'_meet'}),
  quiz('이 사람에게 뭘 해줄까?',r.give.map(x=>({label:x.label,but:x.but})),pickGive,'road',{wounded:true,close:true,pic:game.role+'_choice'})
 ]);
}
function pickGive(i){
 game.give=i;const r=R[game.role];const c=r.give[i];game.event=c.item;
 queue([
  story('road',c.line,'','',{wounded:true,close:true,change:true,pic:game.role+'_care'+i,inventoryApply:{stage:'give',choice:i}}),
  story('road','그런데 이 사람은 혼자 걸을 수가 없어.\n이제 어떻게 데려가지?','', '',{wounded:true,pic:game.role+'_care'+i}),
  story('road',game.role==='priest'?'“나한테는 짐승도 없는데, 어떻게 옮기지?”':game.role==='samaritan'?'“나귀에 타게 하려면 짐을 옮겨야 하는데…”':'“수레에 자리가 없잖아. 대추야자는 어떡하지?”',r.name,'worry',{wounded:true,pic:game.role+'_care'+i}),
  quiz('어떻게 함께 갈까?',r.move.map(x=>({label:x.label,but:x.but})),pickCarry,'road',{wounded:true})
 ]);
}
function pickCarry(i){
 game.carry=i;const r=R[game.role];const c=r.move[i];game.event=c.item;
 queue([
  story('road',c.line,'','',{wounded:true,change:true,pic:game.role+'_carry'+i,inventoryApply:{stage:'carry',choice:i}}),
  story('road',game.role==='priest'&&i===1?'한 걸음, 또 한 걸음. 넘어지지 않도록 서로를 꼭 붙잡았어.\n해가 질 무렵, 마침내 작은 주막이 보였지.':'서로 힘을 보태 길을 내려갔어.\n해가 질 무렵, 작은 주막이 보였지.','', '',{pose:'walk',sunset:true,timeOfDay:'sunset',pic:game.role+'_carry'+i}),
  story('inn',common.inn,'','',{inn:true,pic:game.role+'_inn'}),
  ...((game.role==='priest'&&game.give===1)||(game.role==='merchant'&&game.give===0)?[story('inn','주막 안은 따뜻했어. 겉옷과 짐을 한쪽에 놓고 나그네 곁으로 갔지.','','',{inn:true,pic:game.role+'_inn'})]:[]),
  story('inn',common.keeper,'주막 주인','worry',{inn:true,keeper:true,pic:game.role+'_inn'}),
  story('inn','주막까지 왔어. 그런데 이 사람은 오늘 밤에도 누군가 도와줘야 한대.','', '',{inn:true,pic:game.role+'_inn'}),
  quiz('오늘 밤엔 이 사람을 어떻게 도와줄까?',[
   {label:'남은 은전을 맡기고 내일 다시 온다.',but:'하지만 앞으로 쓸 여행 경비가 없어.',tag:'money'},
   {label:'오늘 밤 이 사람 곁에 남는다.',but:'하지만 내일 해야 할 일도 미뤄야 해.',tag:'night'}
  ],pickFinal,'inn',{inn:true,keeper:true,pic:game.role+'_inn'})
 ]);
}
function pickFinal(i){
 game.final=i;const r=R[game.role];const moneyLine=game.role==='merchant'?'상인은 남은 은전을 주막 주인에게 맡겼어. 가족에게 가져갈 돈은 줄었지만, 내일 다시 오기로 했지.':game.role==='priest'?'제사장은 남은 은전을 주막 주인에게 건넸어. 내일 다시 오겠다는 약속도 남겼지.':'여행자는 남은 은전을 내놓았어. 내일 다시 와서 필요한 것을 챙기기로 했지.';
 const nightLine=game.role==='merchant'?'상인은 수레를 세워두고 밤새 나그네 곁을 지켰어. 내일 장사도 미루기로 했지.':game.role==='priest'?'제사장은 집으로 돌아가는 대신 주막에 남았어. 밤새 물을 떠 오며 나그네 곁을 지켰지.':'여행자는 나귀를 묶어두고 주막에 남았어. 밤새 나그네 곁을 지켰지.';
 const losses={
  priest:[game.give===0?'외투를 벗어주었고':'물주머니의 물을 내어주었고',game.carry===0?'은전 한 닢도 썼어.':'나그네를 부축하느라 온몸이 지쳤어.'],
  samaritan:[game.give===0?'기름과 포도주를 꺼냈고':'물과 여행용 천을 사용했고',game.carry===0?'무거운 짐을 등에 메었어.':'짐보따리 하나를 길에 남겼어.'],
  merchant:[game.give===0?'광주리의 포장천을 풀었고':'자기 외투를 벗어주었고',game.carry===0?'대추야자 한 광주리를 길에 남겼어.':'짐꾼에게 은전도 건넸어.']
 };
 const detail=losses[game.role].join('\n');
 queue([
  ...(game.returned?[story('inn','처음에는 지나쳤지만 다시 돌아왔어.\n지금은 이 사람을 도울 수 있어서 다행이야.','', '',{inn:true,pic:game.role+'_inn'})]:[]),
  story('inn',i===0?moneyLine:nightLine,'','',{inn:true,keeper:true,pic:game.role+'_last'+i,timeOfDay:i===1?'night':'sunset',inventoryApply:{stage:'final',choice:i}}),
  story('inn',i===0?'주막 주인이 고개를 끄덕였어.\n“알겠소. 내일도 제가 챙기겠소.”':'주막 주인이 이불을 가져왔어.\n둘이서 함께 밤을 지켰지.','', '',{inn:true,keeper:true,timeOfDay:i===1?'night':'sunset',pic:game.role+'_last'+i}),
  story('inn',i===0?'밖은 어느새 어두워졌어. 주막에서 잠시 쉬고, 다음 날 아침 길을 나섰지.':'긴 밤이 지나고 아침이 밝았어. 나그네를 주막 주인에게 부탁하고 길을 나섰지.','','',{inn:true,pic:game.role+'_inn',timeOfDay:'morning',timePassage:i===1?'vigil':'rest',missionExpired:true}),
  ...r.lose.map(x=>story(x.bg,x.line,'','',{night:true,pic:game.role+'_lose'})),
  story('city',detail,'','',{night:true,pic:game.role+'_lose'}),
  ending('미션 실패!','하지만 좋은 이웃이 되었어.',''), reflection()
 ]);
}
function current(){return game.queue[game.step]}
function next(){if(renderPending||passageActive)return;const t=current()?.type;if(t!=='story'&&t!=='ending')return;game.step=Math.min(game.queue.length-1,game.step+1);render()}
function restart(){game={dayPhase:'day',missionExpired:false,clockScene:null,inventoryProgress:{give:null,carry:null,final:null,trade:null},role:null,route:null,returned:false,give:null,carry:null,final:null,step:0,queue:[],event:'',scene:'select'};render()}
function mk(tag,cls,txt){const n=document.createElement(tag);if(cls)n.className=cls;if(txt!==undefined)n.textContent=txt;return n}
function getFace(s){if(s.face==='wounded')return ART.wounded;if(s.face)return ART[s.face];const role=game.role;return ART[role+'_'+(s.expr||'normal')]}


// Only a displayed action commits a change. A choice or an earlier reflection does not.
const INVENTORY_ICONS={
 cloak:'<path d="M11 4h10l2 7 6 15-9 3-4-4-4 4-9-3 6-15z"/><path d="M11 4q5 7 10 0M16 9v15M8 18l4 8M24 18l-4 8"/>',
 water:'<path d="M12 4h8v6l5 8v7q-9 7-18 0v-7l5-8z"/><path d="M11 7h10M8 20q8-3 16 0M12 3h8"/>',
 oil:'<path d="M5 5h7v6l3 5v12H2V16l3-5zM22 3h6v7l2 6v12H18V16l4-6z"/><path d="M3 19h11M19 19h10M5 8h7M22 6h6"/>',
 cloth:'<path d="M5 6h22v20H5zM5 11h22M10 11v15M5 21h22M23 11v15"/><path d="M2 26h28"/>',
 coins:'<ellipse cx="11" cy="11" rx="8" ry="6"/><path d="M3 11v6q8 8 16 0v-6M3 17v6q8 8 16 0v-6"/><ellipse cx="23" cy="21" rx="6" ry="7"/><path d="M11 8v6M23 18v6"/>',
 bundle:'<path d="M9 8l-3-5 10 3 10-3-3 5 5 8v11q-12 5-24 0V16z"/><path d="M9 8h14M5 18h22M16 9v20M9 13l14 13M23 13L9 26"/>',
 donkey:'<path d="M6 15h15l3-5 5 4v7l-6-1-2 8h-3v-7H9v7H6zM24 11V3l3 6M27 12l3-8v10M6 15l-4-3v9"/>',
 basket:'<path d="M4 13h24l-3 16H7zM3 10h26v4H3zM8 10q0-9 8-9t8 9M8 18h16M7 23h18M12 14l1 14M20 14l-1 14"/>'
};
function inventoryItems(state=game.inventoryProgress,role=game.role,area=current()?.bg){
 if(!role)return [];
 const g=state.give,c=state.carry,f=state.final;
 const item=(id,name,icon,status,kind='held',extra={})=>({id,name,icon,status,kind,...extra});
 const usedCoins=(role==='priest'&&c===0)||(role==='merchant'&&c===1);
 const coin=()=>item('coins','은전','coins',f===0?'주막에 맡김':usedCoins?'일부 사용':'여행 경비',f===0?'spent':usedCoins?'partial':'held');
 if(role==='priest')return [
  item('cloak','외투','cloak',g===0?'덮어줌':c!==null?'가지고 있어':'입고 있어',g===0?'spent':'held'),
  item('water','물주머니','water',g===1?'물이 적음':'물이 있어',g===1?'partial':'held',g===1?{level:25}:{}),coin()
 ];
 if(role==='samaritan')return [
  item('oil','기름·포도주','oil',g===0?'일부 사용':'챙겨 왔어',g===0?'partial':'held'),
  item('water','물주머니','water',g===1?'물이 적음':'물이 있어',g===1?'partial':'held',g===1?{level:25}:{}),
  item('bundle','짐보따리','bundle',c===null?'나귀에 실음':c===1?'길에 남김':area==='inn'?'한쪽에 둠':area==='city'?'가지고 있어':'등에 멤',c===1?'spent':'held'),
  item('donkey','나귀','donkey',c===null?'짐을 싣고 있어':area==='inn'?'밖에 매어 둠':area==='city'?'함께 왔어':'나그네가 타고 있어'),coin()
 ];
 const traded=state.trade===0;
 return [
  item('cloak','외투','cloak',g===1?'덮어줌':c!==null?'가지고 있어':'입고 있어',g===1?'spent':'held'),
  item('cloth','포장천','cloth',g===0?'상처 감쌈':'광주리에 있어',g===0?'spent':'held'),
  item('baskets','대추야자','basket',traded?'구매자에게 팖':c===null?'수레에 실음':c===0?'1개 길에 남김':'수레 2 · 짐꾼 1',traded?'spent':c===0?'partial':'held',{count:traded?0:c===0?2:3}),
  traded?item('coins','은전','coins','판매 대금'):coin()
 ];
}
function inventoryMessage(stage,choice){
 if(stage==='trade')return '대추야자 세 광주리를 팔았어.';
 if(stage==='final')return choice===0?'남은 은전을 주막 주인에게 맡겼어.':'밤새 나그네 곁을 지켰어.';
 if(stage==='give')return {
  priest:['외투를 나그네에게 덮어줬어.','물과 천을 꺼내 사용했어.'],
  samaritan:['기름·포도주와 천을 사용했어.','물과 천을 꺼내 사용했어.'],
  merchant:['광주리의 포장천을 풀어 사용했어.','외투를 나그네에게 덮어줬어.']
 }[game.role][choice];
 return {
  priest:['은전 일부로 짐승을 빌렸어.','먼 길을 부축해서 걸었어.'],
  samaritan:['나귀의 짐을 내 등에 멨어.','짐보따리 하나를 길에 남겼어.'],
  merchant:['광주리 하나를 길에 남겼어.','은전을 주고 광주리 하나를 짐꾼에게 맡겼어.']
 }[game.role][choice];
}

function energyLevel(state=game.inventoryProgress,role=game.role){
 const carriedByMe=(role==='priest'&&state.carry===1)||(role==='samaritan'&&state.carry===0);
 return Math.max(1,3-(carriedByMe?1:0)-(state.final===1?1:0));
}
function renderEnergy(){
 const host=$('inventoryEnergy');
 if(!game.role){host.replaceChildren();delete host.dataset.level;host.className='inventory-energy';return}
 const level=energyLevel();
 if(host.dataset.level===String(level))return;
 const previous=host.dataset.level===undefined?3:Number(host.dataset.level);
 host.dataset.level=String(level);host.replaceChildren();
 host.className='inventory-energy'+(level<previous?' has-changed':'');
 host.setAttribute('aria-valuenow',String(level));
 host.setAttribute('aria-valuetext','기운 3칸 중 '+level+'칸');
 host.appendChild(mk('span','energy-label','기운'));
 const bars=mk('span','energy-bars');bars.setAttribute('aria-hidden','true');
 for(let i=0;i<3;i++)bars.appendChild(mk('span','energy-segment'+(i>=level?' is-empty':'')+(i>=level&&i<previous?' just-used':'')));
 host.appendChild(bars);
}

function renderInventory(s){
 const progress=game.inventoryProgress;
 const visible=!!game.role&&s?.type!=='ending'&&s?.type!=='reflection';
 $('inventory').classList.toggle('hide',!visible);
 if(!game.role){$('inventorySlots').replaceChildren();delete $('inventorySlots').dataset.signature;$('inventoryUpdate').textContent='';renderEnergy();return}
 const old=inventoryItems();let message='',committed=false;
 if(s?.inventoryApply){
  const {stage,choice}=s.inventoryApply;
  if(progress[stage]!==choice){progress[stage]=choice;message=inventoryMessage(stage,choice);committed=true}
 }
 renderEnergy();
 const items=inventoryItems();const host=$('inventorySlots');
 host.style.setProperty('--slot-count',String(items.length));
 const signature=JSON.stringify(items);
 if(host.dataset.signature!==signature){
  host.replaceChildren();host.dataset.signature=signature;
  items.forEach((item,index)=>{
   const changed=JSON.stringify(old[index])!==JSON.stringify(item);
   const cell=mk('div','inventory-slot is-'+item.kind+(changed?' has-changed':''));
   cell.setAttribute('role','listitem');cell.setAttribute('aria-label',item.name+' · '+(item.count!==undefined?item.count+'개 · ':'')+item.status);
   const icon=mk('span','inventory-icon');icon.setAttribute('aria-hidden','true');
   icon.innerHTML='<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+INVENTORY_ICONS[item.icon]+'</svg>';
   if(item.count!==undefined)icon.appendChild(mk('span','inventory-count','×'+item.count));
   const copy=mk('span','inventory-copy');copy.appendChild(mk('span','inventory-name',item.name));
   cell.appendChild(icon);cell.appendChild(copy);
   if(item.level!==undefined){const meter=mk('span','inventory-meter');meter.setAttribute('aria-hidden','true');const fill=mk('span');fill.style.width=item.level+'%';meter.appendChild(fill);cell.appendChild(meter)}
   host.appendChild(cell);
  });
 }
 if(committed&&!message)$('inventoryUpdate').textContent='';
 if(message){
  const notice=$('inventoryUpdate');notice.textContent=message;notice.style.animation='none';
  void notice.offsetWidth;notice.style.animation='';
 }
}

function pictureFor(s){
 if(!s)return 'vista';
 if(s.type==='reflection')return 'reflection';
 let key=s.pic||((s.type==='ending')?game.role+'_'+(game.route==='mission'?'win':'lose'):s.bg||'road');
 if(/_(meet|choice)$/.test(key))return 'discovery';
 if(/_carry[01]$/.test(key)&&game.role!=='samaritan')return key+'_g'+game.give;
 if(s.wounded&&!s.pic)return game.give===null?'discovery':game.role+'_care'+game.give;
 return key;
}


// Keep the injured traveler to the right of the person helping him.
// Mirror only the illustration, without changing text or controls.
const MIRRORED_PICTURES=new Set([
 'merchant_care1','priest_care1',
 'priest_carry0_g0','priest_carry0_g1','priest_last1',
 'samaritan_care0','samaritan_care1',
 'samaritan_carry0','samaritan_carry1','samaritan_last0'
]);
let renderRevision=0,renderPending=false,passageActive=false,passageTimer=null;
const artLoads=new Map();
function prepareArt(key){
 const src=ART[key];
 if(!src)return Promise.resolve();
 if(!artLoads.has(src)){
  const image=new Image();image.src=src;
  const ready=image.decode().catch(error=>{artLoads.delete(src);throw error});
  artLoads.set(src,ready);
 }
 return artLoads.get(src);
}
function stopTimePassage(){
 clearTimeout(passageTimer);passageTimer=null;passageActive=false;
 $('timePassage').classList.add('hide');
 $('viewport').classList.remove('is-time-passage');
}
function renderClock(s){
 const label=$('missionName'),deadline=$('missionDeadline'),passage=$('timePassage');
 if(!s){
  $('viewport').dataset.dayPhase='day';
  label.classList.toggle('mission-expired',false);label.classList.toggle('just-expired',false);
  deadline.classList.add('hide');deadline.textContent='';stopTimePassage();return;
 }
 const newlyExpired=!game.missionExpired&&!!s.missionExpired;
 if(s.timeOfDay)game.dayPhase=s.timeOfDay;
 if(s.missionExpired)game.missionExpired=true;
 $('viewport').dataset.dayPhase=game.dayPhase;
 label.classList.toggle('mission-expired',game.missionExpired);
 if(newlyExpired)label.classList.add('just-expired');
 else if(!game.missionExpired)label.classList.toggle('just-expired',false);
 deadline.classList.toggle('hide',!game.missionExpired);
 const message=game.missionExpired?'약속한 시간이 지났어.':'';
 if(deadline.textContent!==message)deadline.textContent=message;
 if(s.bg==='inn'&&s.type==='story'){
  const phase={day:'낮',sunset:'해 질 무렵',night:'밤',morning:'아침'}[game.dayPhase];
  $('stageMark').textContent='주막 · '+phase;
 }
 if(game.clockScene!==s){
  stopTimePassage();
  game.clockScene=s;
  if(s.timePassage&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
   passageActive=true;
   passage.className='time-passage';
   $('viewport').classList.add('is-time-passage');
   passageTimer=setTimeout(()=>{if(current()===s)stopTimePassage()},1600);
  }
 }
}

async function render(){
 const revision=++renderRevision;
 const s=current();const role=game.role;const r=R[role];const select=!s;
 const pic=pictureFor(s);
 renderPending=true;
 $('viewport').setAttribute('aria-busy','true');
 let pictureReady=false;
 try{await prepareArt(pic);pictureReady=true}catch(error){/* Keep the previous picture if loading fails. */}
 if(revision!==renderRevision)return;
 renderPending=false;
 $('viewport').setAttribute('aria-busy','false');
 $('start').classList.toggle('hide',!select);$('storyPanel').classList.toggle('hide',select||s.type!=='story');$('choicePanel').classList.toggle('hide',select||s.type!=='quiz');$('endingPanel').classList.toggle('hide',select||s.type!=='ending');$('reflectionPanel').classList.toggle('hide',select||s.type!=='reflection');
 renderInventory(s);
 if(pictureReady){
  $('bg').style.backgroundImage='url('+JSON.stringify(ART[pic]) +')';
  $('bg').classList.toggle('is-mirrored',MIRRORED_PICTURES.has(pic));
 }
 $('viewport').className='viewport '+(select?'on-start':s.type==='ending'?'on-ending':s.type==='reflection'?'on-reflection':s.type==='quiz'?'on-choice':'on-story')+' scene-'+(s?.bg||'vista')+(s?.close?' close-shot':'')+(s?.sunset?' sunset':'')+(s?.carrying?' on-carry':'');
 $('roleName').textContent=r?r.name:'미션! 여리고 가는 길';$('missionName').textContent=r?r.mission:'누구의 이야기를 시작할까?';
 $('stageMark').textContent=select?'시작':s.type==='ending'||s.type==='reflection'?'이야기의 끝':s.type==='quiz'?'선택의 순간':({city:'여리고',inn:'길가의 주막',road:'광야길'}[s.bg]||'여리고로 가는 길');
 $('hero').className='actor hero '+(role||'')+' '+(s?.pose||'');$('hero').src=role?ART[role]:'';
 $('hero').classList.add('hide');
 $('wounded').src=ART.wounded;
 const showWounded=false;
 $('wounded').className='actor wounded '+(showWounded&&!s?.pic?'':'hide')+(s?.carrying?' passenger':'');
 $('keeper').classList.add('hide'); // 별도 원화 없이 이질적인 사람 이모지를 얹지 않음
 $('loss').classList.add('hide'); // 대사와 같은 내용을 중복 표기하지 않음
 
 renderClock(s);
 // Decode upcoming pictures without replacing the scene currently on screen.
 for(const upcoming of game.queue.slice(game.step+1,game.step+4))prepareArt(pictureFor(upcoming)).catch(()=>{});
 if(select){renderStart();return}
 if(s.type==='story'){
  const speaking=!!s.speaker && s.speaker===R[game.role].name && game.give===null;
  $('speaker').textContent=s.speaker||'';$('portrait').classList.toggle('hide',!speaking);if(speaking)$('portrait').src=getFace(s);
  $('dialogue').textContent=s.line;$('next').textContent=game.step===game.queue.length-2?'마지막 ▶':'다음 ▶';
 }else if(s.type==='quiz'){
  $('question').textContent=s.title;const opt=$('options');opt.replaceChildren();
  s.options.forEach((o,i)=>{
   const b=mk('button','option');b.type='button';b.dataset.index=i;
   const num=mk('span','option-num',String(i+1));
   const lines=mk('span','option-lines');lines.appendChild(mk('strong','',o.label));lines.appendChild(mk('span','option-but',o.but));
   b.appendChild(num);b.appendChild(lines);b.addEventListener('click',()=>s.callback(i));opt.appendChild(b)
  })
 }else if(s.type==='ending'){
  $('endTitle').textContent=s.title;$('endSubtitle').textContent=s.subtitle;
  $('endStory').textContent=s.storyText||'';$('endStory').classList.toggle('hide',!s.storyText);
  $('endingPortrait').src=ART[role+'_resolve'];
  $('endRole').textContent=r.name;
 }
}
function renderStart(){
 const host=$('roles');if(host.children.length)return;
 ['priest','samaritan','merchant'].forEach((key,i)=>{
  const r=R[key];const b=mk('button','role-card');b.type='button';
  const image=mk('img','role-portrait');image.src=ART[key];image.alt='';b.appendChild(image);
  b.appendChild(mk('strong','role-title',r.name));b.appendChild(mk('span','role-mission',r.mission));
  b.appendChild(mk('span','role-number','선택 '+(i+1)));
  b.addEventListener('click',()=>chooseRole(key));host.appendChild(b)
 })
}
$('next').addEventListener('click',next);$('again').addEventListener('click',next);$('reflectionRestart').addEventListener('click',restart);$('reset').addEventListener('click',restart);
async function toggleFullscreen(){
 try{
  if(document.fullscreenElement)await document.exitFullscreen?.();
  else if(document.querySelector('.shell').requestFullscreen)await document.querySelector('.shell').requestFullscreen();
 }catch(error){
  $('fullscreen').title='이 브라우저에서는 전체화면을 사용할 수 없어요.';
 }
}
$('fullscreen').addEventListener('click',toggleFullscreen);
if(!document.fullscreenEnabled)$('fullscreen').classList.add('hide');
document.addEventListener('fullscreenchange',()=>{
 const active=!!document.fullscreenElement;
 $('fullscreen').setAttribute('aria-pressed',String(active));
 $('fullscreen').setAttribute('aria-label',active?'전체화면 종료':'전체화면');
});
$('storyPanel').addEventListener('click',ev=>{if(!ev.target.closest('button'))next()});
document.addEventListener('click',ev=>{
 if((renderPending||passageActive)&&!ev.target.closest('#reset,#fullscreen')){
  ev.preventDefault();ev.stopImmediatePropagation();
 }
},true);
document.addEventListener('keydown',ev=>{
 if(['INPUT','TEXTAREA'].includes(document.activeElement?.tagName))return;
 if(ev.ctrlKey||ev.altKey||ev.metaKey||ev.repeat)return;
 if((renderPending||passageActive)&&!['r','R','f','F'].includes(ev.key)){ev.preventDefault();return}
 if((ev.key===' '||ev.key==='Enter')&&document.activeElement?.closest('button'))return;
 if(ev.key==='f'||ev.key==='F'){$('fullscreen').click();return}
 if((ev.key===' '||ev.key==='Enter')&&['story','ending'].includes(current()?.type)){ev.preventDefault();next();return}
 if(ev.key==='r'||ev.key==='R'){restart();return}
 if(['1','2','3'].includes(ev.key)){
  const idx=Number(ev.key)-1;
  if(!current())$('roles').querySelectorAll('button')[idx]?.click();
  else if(current().type==='quiz')$('options').querySelectorAll('button')[idx]?.click()
 }
});
render();
