const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs'),path=require('path'),http=require('http');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'qa');fs.mkdirSync(output,{recursive:true});
const report={captions:[],coldLoad:null,errors:[]};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const server=http.createServer(async(req,res)=>{
 const name=decodeURIComponent(new URL(req.url,'http://local').pathname);
 if(name==='/assets/priest_care0.webp')await pause(900);
 const file=path.join(root,name==='/'?'index.html':name);
 if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
 try{
  res.setHeader('Cache-Control','no-store');
  res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.webp')?'image/webp':'text/html');
  res.end(await fs.promises.readFile(file));
 }catch{res.writeHead(404);res.end()}
});
async function ready(page){await page.waitForFunction(()=>document.querySelector('main')?.getAttribute('aria-busy')==='false')}
async function advance(page){
 await ready(page);
 while(await page.locator('#storyPanel').isVisible()){
  await page.locator('#next').click();await ready(page);
 }
}
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const local='http://127.0.0.1:'+server.address().port+'/';
 const url=process.env.BASE_URL||local;
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  for(const [device,width,height] of [['desktop',1920,1080],['mobile',390,844]])for(let role=0;role<3;role++)for(let final=0;final<2;final++){
   const page=await browser.newPage({viewport:{width,height}});
   page.on('pageerror',e=>report.errors.push(String(e)));
   await page.goto(url);await ready(page);
   await page.locator('.role-card').nth(role).click();await advance(page);
   await page.locator('.option').nth(1).click();await advance(page);
   await page.locator('.option').nth(0).click();await advance(page);
   await page.locator('.option').nth(0).click();await advance(page);
   await page.locator('.option').nth(final).click();await ready(page);
   await page.locator('#next').click();await ready(page);
   await page.locator('#next').click();await ready(page);
   await page.locator('#viewport.is-time-passage').waitFor();
   const before=await page.locator('#dialogue').textContent();
   const captionCount=await page.locator('#timePassage span').count();
   if(captionCount!==1||await page.locator('#storyPanel').isVisible())throw Error('Caption overlaps dialogue');
   await page.mouse.click(width/2,height/2);
   await page.keyboard.press('Enter');await page.keyboard.press('Space');await page.keyboard.press('1');
   if(await page.locator('#dialogue').textContent()!==before)throw Error('Caption click or key skipped morning');
   if(device==='mobile'&&role===1&&final===1){await pause(350);await page.screenshot({path:path.join(output,'morning-caption.png'),fullPage:true})}
   await page.locator('#timePassage').waitFor({state:'hidden'});
   if(!await page.locator('#storyPanel').isVisible())throw Error('Dialogue not restored');
   if(await page.locator('#dialogue').textContent()!==before)throw Error('Morning dialogue lost');
   await page.locator('#next').click();await ready(page);
   if(await page.locator('#dialogue').textContent()===before)throw Error('Cannot continue after caption');
   report.captions.push({device,role,final,captionCount,passed:true});
   await page.close();
  }
  // A slow, uncached picture must not replace the previous frame before decoding.
  const page=await browser.newPage({viewport:{width:390,height:844}});
  await page.goto(local);await ready(page);await page.locator('.role-card').nth(0).click();await advance(page);
  await page.locator('.option').nth(1).click();await advance(page);
  const previous=await page.locator('#bg').getAttribute('style');
  await page.locator('.option').nth(0).click();
  if(await page.locator('#viewport').getAttribute('aria-busy')!=='true')throw Error('Slow image not pending');
  if(await page.locator('#bg').getAttribute('style')!==previous)throw Error('Background changed before image ready');
  await page.keyboard.press('Enter');await page.keyboard.press('Space');
  await ready(page);
  if(!(await page.locator('#bg').getAttribute('style')).includes('priest_care0'))throw Error('New picture not committed');
  if(!(await page.locator('#dialogue').innerText()).includes('외투를 벗어'))throw Error('Loading input skipped scene');
  report.coldLoad={delayMs:900,keptPreviousFrame:true,noSkippedScene:true};
  // Reset cancels a pending scene; its late image must never overwrite the start.
  await page.reload();await ready(page);await page.locator('.role-card').nth(0).click();await advance(page);
  await page.locator('.option').nth(1).click();await advance(page);await page.locator('.option').nth(0).click();
  await page.keyboard.press('r');await ready(page);await pause(1100);
  if(!await page.locator('#start').isVisible()||!(await page.locator('#bg').getAttribute('style')).includes('vista'))throw Error('Late render overwrote reset');
  report.resetDuringLoad=true;
  const reduced=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
  await reduced.goto(local);await ready(reduced);await reduced.locator('.role-card').nth(0).click();await advance(reduced);
  await reduced.locator('.option').nth(1).click();await advance(reduced);await reduced.locator('.option').nth(1).click();await advance(reduced);await reduced.locator('.option').nth(1).click();await advance(reduced);await reduced.locator('.option').nth(1).click();await ready(reduced);
  await reduced.locator('#next').click();await ready(reduced);await reduced.locator('#next').click();await ready(reduced);
  if(await reduced.locator('#timePassage').isVisible()||!await reduced.locator('#storyPanel').isVisible())throw Error('Reduced motion blocked');
  report.reducedMotion=true;
 }finally{await browser.close();server.close()}
 fs.writeFileSync(path.join(output,'transition-results.json'),JSON.stringify(report,null,2));console.log(report);
 if(report.errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);server.close();process.exit(1)});
