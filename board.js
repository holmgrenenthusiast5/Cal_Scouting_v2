const el=id=>document.getElementById(id);
const format=n=>n==null?'N/A':n.toFixed(2);
const pct=n=>n==null?'N/A':n.toFixed(1)+'%';
const escapeText=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ranks={};
for(const col of [4,5,9,10,11,12,13,14,15]){
 const sorted=players.map(p=>p[col]).filter(n=>n!=null).sort((a,b)=>b-a);
 ranks[col]=new Map();
 sorted.forEach((v,i)=>{if(!ranks[col].has(v))ranks[col].set(v,i+1)});
}
let page=0;
for(const grade of [...new Set(players.map(p=>p[3]))].sort())el('grade').add(new Option(grade,grade));
function showPlayer(i){
 const p=players[i], text=escapeText;
 const metrics=[['Overall',4,5],['Offense',11,13],['Defense',12,14]];
 const cell=c=>p[c]==null?'N/A':format(p[c])+' · #'+ranks[c].get(p[c]);
 el('bio').innerHTML='<div class="eyebrow">Player profile</div><h2>'+text(p[0])+'</h2><p>'+text(p[3])+' · '+text(p[2])+'<br>2025–26 performance at '+text(p[1])+'</p><div class="stats"><div><strong>'+pct(p[9])+'</strong>Above ACC median</div><div><strong>'+pct(p[10])+'</strong>All ACC Level Impact</div></div><h3>Measured impact</h3><table><thead><tr><th>2025–26</th><th>Halo · rank</th><th>Revised · rank</th></tr></thead><tbody>'+metrics.map(([k,a,b])=>'<tr><td>'+k+'</td><td>'+cell(a)+'</td><td>'+cell(b)+'</td></tr>').join('')+'<tr><td>Board percentile</td><td>'+format(p[7])+'</td><td>'+format(p[8])+'</td></tr></tbody></table>'+(p[5]==null?'<p>Revised player match unresolved. ACC probabilities unavailable.</p>':'');
 el('profile').showModal();
}
function draw(){
 const revised=+el('source').value, off=revised?13:11, def=off+1,total=4+revised;
 const choice=el('sort').value,c=({off,def,total})[choice]??Number(choice);
 const q=el('query').value.toLowerCase().trim(),grade=el('grade').value;
 const filtered=players.map((p,i)=>({p,i})).filter(({p})=>(!grade||p[3]===grade)&&p.slice(0,3).join(' ').toLowerCase().includes(q)).sort((a,b)=>(b.p[c]??-Infinity)-(a.p[c]??-Infinity)||a.p[0].localeCompare(b.p[0]));
 const start=page*25, odds=n=>'<span class="odds">'+pct(n)+'</span>'+(n==null?'':'<span class="bar"><i style="width:'+n+'%"></i></span>');
 el('rows').innerHTML=filtered.slice(start,start+25).map(({p,i})=>'<tr><td>'+(ranks[c].get(p[c])??'N/A')+'</td><td><button data-player="'+i+'">'+escapeText(p[0])+'</button><small>'+escapeText(p[2])+'</small></td><td>'+escapeText(p[3])+'</td><td>'+odds(p[9])+'</td><td>'+odds(p[10])+'</td><td>'+format(p[off])+'</td><td>'+format(p[def])+'</td><td>'+format(p[total])+'</td><td>'+format(p[7+revised])+'</td><td>'+(p[15]??'N/A')+'</td></tr>').join('');
 el('count').textContent=filtered.length?(start+1)+'–'+Math.min(start+25,filtered.length)+' of '+filtered.length+' players':'No players match these filters.';
 el('prev').disabled=page===0;el('next').disabled=start+25>=filtered.length;
}
for(const id of ['query','grade','sort','source'])el(id).addEventListener('input',()=>{page=0;draw()});
el('prev').onclick=()=>{page--;draw()};el('next').onclick=()=>{page++;draw()};
el('rows').onclick=e=>{const b=e.target.closest('[data-player]');if(b)showPlayer(+b.dataset.player)};
draw();


