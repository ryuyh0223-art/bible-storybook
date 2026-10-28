const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('fs');
const path = require('path');
const url = process.env.BASE_URL || 'file:///' + path.resolve(__dirname, '../index.html').replaceAll('\\','/');
const out = path.resolve(__dirname, '../qa');
fs.mkdirSync(out,{recursive:true});
const results = {routes:[],issues:[],errors:[],images:[],screenshots:[]};
async function audit(page,label){
 const issues=await page.evaluate(()=>{
  const issues=[];const main=document.querySelector('main').getBoundingClientRect();
  if(document.querySelector('main').dataset.dayPhase==='morning'&&!document.querySelector('#missionName').classList.contains('mission-expired'))issues.push('Morning deadline not reflected');
  for(const e of document.querySelectorAll('button,.dialogue,.question,.end-title,.end-sub,.role-mission,.reflection-question,.controls-help')){
   if(!e.checkVisibility())continue;
   const r=e.getBoundingClientRect();
   if(r.width<1||r.height<1)continue;
   if(r.left < -1 || r.right > innerWidth+1)issues.push('horizontal: '+e.className);
   if(e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2)issues.push('text overflow: '+e.className+' '+e.clientWidth+'/'+e.scrollWidth+' '+e.clientHeight+'/'+e.scrollHeight);
   if(r.top<main.top-1||r.bottom>main.bottom+1)issues.push('outside game: '+e.className);
  }
  return issues;
 });
 for(const issue of issues)results.issues.push({label,issue});
}
async function shot(page,name){await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});results.screenshots.push(name+'.png')}
async function run(page,role,choices,label,capture=false,keyboard=false){
 await page.goto(url);
 if(capture)await shot(page,label+'-start');
 if(keyboard)await page.locator('body').press(String(role+1));else await page.locator('.role-card').nth(role).click();
 let decision=0,steps=0,end='';
 while(++steps<100){
  await audit(page,label+':'+steps);
  if(await page.locator('#storyPanel').isVisible()){
   if(capture&&steps===1)await shot(page,label+'-story');
   if(keyboard)await page.locator('body').press(steps%2?'Enter':'Space');else await page.locator('#next').click();
  }else if(await page.locator('#choicePanel').isVisible()){
   if(capture&&decision===0)await shot(page,label+'-choice');
   const choice=choices[decision++];if(choice===undefined)throw Error('Missing choice '+label);
   if(keyboard)await page.locator('body').press(String(choice+1));else await page.locator('.option').nth(choice).click();
  }else if(await page.locator('#endingPanel').isVisible()){
   end=await page.locator('#endTitle').innerText();
   if(end!==(choices.length===2?'미션 성공!':'미션 실패!'))throw Error('Wrong ending '+label);
   if(capture)await shot(page,label+'-ending');
   await page.locator('#again').click();
  }else if(await page.locator('#reflectionPanel').isVisible()){
   if(capture)await shot(page,label+'-reflection');
   await page.locator('#reflectionRestart').click();
   if(!await page.locator('#start').isVisible())throw Error('Restart failed');
   results.routes.push({label,role,choices,end,steps});return;
  }else throw Error('Unknown screen '+label);
 }
 throw Error('Route stuck '+label);
}
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const sizes=process.env.QUICK?[['desktop',1920,1080,false]]:[['desktop',1920,1080,true],['mobile',390,844,true],['small-mobile',320,568,false],['landscape',844,390,false],['tablet',768,1024,false],['laptop',1366,768,false]];
 for(const [label,width,height,all] of sizes){
  const page=await browser.newPage({viewport:{width,height},isMobile:width<900,hasTouch:width<900});
  page.on('pageerror',e=>results.errors.push({label,error:String(e)}));
  page.on('console',m=>{if(m.type()==='error')results.errors.push({label,error:m.text()})});
  await run(page,0,[0,0],label+'-mission',true,true);
  for(let role=0;role<3;role++){
   if(role>0&&all)await run(page,role,[0,0],label+'-'+role+'-mission');
   for(const returned of (all?[false,true]:[true]))for(let give=0;give<(all?2:1);give++)for(let carry=0;carry<(all?2:1);carry++)for(let final=0;final<(all?2:1);final++){
    const choices=returned?[0,1,give,carry,final]:[1,give,carry,final];
    await run(page,role,choices,label+'-'+role+'-'+choices.join(''),role===1&&returned&&give===0&&carry===0&&final===0);
   }
  }
  await page.close();
  console.log(label+' finished');
 }
 const page=await browser.newPage({viewport:{width:1920,height:1080}});
 await page.goto(url);
 results.images=await page.evaluate(async()=>{
  const images=[];
  for(const [key,src] of Object.entries(ART)){
   const image=new Image();image.src=src;
   try{await image.decode();images.push({key,width:image.naturalWidth,height:image.naturalHeight})}
   catch{images.push({key,error:src})}
   image.src='';
  }
  return images;
 });
 await page.locator('#fullscreen').click();
 results.fullscreen=await page.evaluate(()=>({active:!!document.fullscreenElement,width:innerWidth,height:innerHeight,frame:document.querySelector('main').getBoundingClientRect().toJSON()}));
 await shot(page,'fullscreen');
 await page.locator('body').press('f');
 results.fullscreenExited=await page.evaluate(()=>!document.fullscreenElement);
 // A focused restart button must activate itself, without also advancing a line.
 await page.locator('.role-card').first().click();
 await page.locator('#reset').focus();await page.keyboard.press('Enter');
 results.focusedRestart=await page.locator('#start').isVisible();
 await page.keyboard.press('3');await page.keyboard.press('r');
 results.keyboardRestart=await page.locator('#start').isVisible();
 const touch=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
 await touch.goto(url);await touch.locator('.role-card').nth(1).tap();await touch.locator('#next').tap();
 results.touch=await touch.locator('#dialogue').innerText();
 await browser.close();
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));
 if(results.issues.length || results.errors.length || results.images.some(i=>i.error) || !results.fullscreenExited || !results.focusedRestart || !results.keyboardRestart)process.exitCode=1;
 console.log(JSON.stringify({routes:results.routes.length,issues:results.issues.length,errors:results.errors,brokenImages:results.images.filter(i=>i.error),fullscreen:results.fullscreen,fullscreenExited:results.fullscreenExited,focusedRestart:results.focusedRestart,keyboardRestart:results.keyboardRestart}));
})().catch(e=>{fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));console.error(e);process.exit(1)});
