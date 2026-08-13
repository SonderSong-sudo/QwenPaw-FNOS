import{p as et}from"./chunk-JWPE2WC7-CJwUdF-a.js";import{aV as at,aU as rt,aW as it,aX as nt,ba as st,b9 as ot,aY as l,a$ as E,aZ as lt,bl as ct,bJ as dt,bK as gt,bL as U,bM as ht,b0 as pt,bb as ut,bN as ft,bm as mt}from"./ui-vendor-D67aqjKF.js";import{p as vt}from"./cynefin-VYW2F7L2-DGUM849d.js";import"./react-vendor-DAURSz_k.js";import"./utils-vendor-DW8wLLZl.js";import"./markdown-vendor-zoJ7LKuz.js";var St=mt.pie,L={sections:new Map,showData:!1},y=L.sections,R=L.showData,xt=structuredClone(St),bt=l(()=>structuredClone(xt),"getConfig"),wt=l(()=>{y=new Map,R=L.showData,ut()},"clear"),$t=l(({label:t,value:a})=>{if(a<0)throw new Error(`"${t}" has invalid value: ${a}. Negative values are not allowed in pie charts. All slice values must be >= 0.`);y.has(t)||(y.set(t,a),E.debug(`added new section: ${t}, with value: ${a}`))},"addSection"),Ct=l(()=>y,"getSections"),Dt=l(t=>{R=t},"setShowData"),yt=l(()=>R,"getShowData"),V={getConfig:bt,clear:wt,setDiagramTitle:ot,getDiagramTitle:st,setAccTitle:nt,getAccTitle:it,setAccDescription:rt,getAccDescription:at,addSection:$t,getSections:Ct,setShowData:Dt,getShowData:yt},Tt=l((t,a)=>{et(t,a),a.setShowData(t.showData),t.sections.map(a.addSection)},"populateDb"),At={parse:l(async t=>{const a=await vt("pie",t);E.debug(a),Tt(a,V)},"parse")},kt=l(t=>`
  .pieCircle{
    stroke: ${t.pieStrokeColor};
    stroke-width : ${t.pieStrokeWidth};
    opacity : ${t.pieOpacity};
  }
  .pieCircle.highlighted{
    scale: 1.05;
    opacity: 1;
  }
  .pieCircle.highlightedOnHover:hover{
    transition-duration: 250ms;
    scale: 1.05;
    opacity: 1;
  }
  .pieOuterCircle{
    stroke: ${t.pieOuterStrokeColor};
    stroke-width: ${t.pieOuterStrokeWidth};
    fill: none;
  }
  .pieTitleText {
    text-anchor: middle;
    font-size: ${t.pieTitleTextSize};
    fill: ${t.pieTitleTextColor};
    font-family: ${t.fontFamily};
  }
  .slice {
    font-family: ${t.fontFamily};
    fill: ${t.pieSectionTextColor};
    font-size:${t.pieSectionTextSize};
    // fill: white;
  }
  .legend text {
    fill: ${t.pieLegendTextColor};
    font-family: ${t.fontFamily};
    font-size: ${t.pieLegendTextSize};
  }
`,"getStyles"),_t=kt,zt=l(t=>{const a=[...t.values()].reduce((s,m)=>s+m,0),W=[...t.entries()].map(([s,m])=>({label:s,value:m})).filter(s=>s.value/a*100>=1);return ft().value(s=>s.value).sort(null)(W)},"createPieArcs"),Et=l((t,a,W,M)=>{var I;E.debug(`rendering pie chart
`+t);const s=M.db,m=lt(),p=ct(s.getConfig(),m.pie),F=40,i=18,c=4,w=450,S=w,T=dt(a),$=T.append("g");$.attr("transform","translate("+S/2+","+w/2+")");const{themeVariables:n}=m;let[H]=gt(n.pieOuterStrokeWidth);H??(H=2);const X=p.legendPosition,O=p.textPosition,Z=p.donutHole>0&&p.donutHole<=.9?p.donutHole:0,u=Math.min(S,w)/2-F,J=U().innerRadius(Z*u).outerRadius(u),K=U().innerRadius(u*O).outerRadius(u*O),x=$.append("g");x.append("circle").attr("cx",0).attr("cy",0).attr("r",u+H/2).attr("class","pieOuterCircle");const C=s.getSections(),Y=zt(C),j=[n.pie1,n.pie2,n.pie3,n.pie4,n.pie5,n.pie6,n.pie7,n.pie8,n.pie9,n.pie10,n.pie11,n.pie12];let A=0;C.forEach(e=>{A+=e});const P=Y.filter(e=>(e.data.value/A*100).toFixed(0)!=="0"),k=ht(j).domain([...C.keys()]);x.selectAll("mySlices").data(P).enter().append("path").attr("d",J).attr("fill",e=>k(e.data.label)).attr("class",e=>{let r="pieCircle";return p.highlightSlice==="hover"?r+=" highlightedOnHover":p.highlightSlice===e.data.label&&(r+=" highlighted"),r}),x.selectAll("mySlices").data(P).enter().append("text").text(e=>(e.data.value/A*100).toFixed(0)+"%").attr("transform",e=>"translate("+K.centroid(e)+")").style("text-anchor","middle").attr("class","slice");const q=$.append("text").text(s.getDiagramTitle()).attr("x",0).attr("y",-400/2).attr("class","pieTitleText"),b=[...C.entries()].map(([e,r])=>({label:e,value:r})),f=$.selectAll(".legend").data(b).enter().append("g").attr("class","legend");f.append("rect").attr("width",i).attr("height",i).style("fill",e=>k(e.label)).style("stroke",e=>k(e.label)),f.append("text").attr("x",i+c).attr("y",i-c).text(e=>s.getShowData()?`${e.label} [${e.value}]`:e.label);const v=Math.max(...f.selectAll("text").nodes().map(e=>(e==null?void 0:e.getBoundingClientRect().width)??0));let D=w,_=S+F;const o=i+c,z=b.length*o;switch(X){case"center":f.attr("transform",(e,r)=>{const d=o*b.length/2,g=-v/2-(i+c),h=r*o-d;return"translate("+g+","+h+")"});break;case"top":D+=z,f.attr("transform",(e,r)=>{const d=u,g=-v/2-(i+c),h=r*o-d;return`translate(${g}, ${h})`}),x.attr("transform",()=>`translate(0, ${z+o})`);break;case"bottom":D+=z,f.attr("transform",(e,r)=>{const d=-u-o,g=-v/2-(i+c),h=r*o-d;return"translate("+g+","+h+")"});break;case"left":_+=i+c+v,f.attr("transform",(e,r)=>{const d=o*b.length/2,g=-u-(i+c),h=r*o-d;return"translate("+g+","+h+")"}),x.attr("transform",()=>`translate(${v+i+c}, 0)`);break;case"right":default:_+=i+c+v,f.attr("transform",(e,r)=>{const d=o*b.length/2,g=12*i,h=r*o-d;return"translate("+g+","+h+")"});break}const G=((I=q.node())==null?void 0:I.getBoundingClientRect().width)??0,Q=S/2-G/2,tt=S/2+G/2,N=Math.min(0,Q),B=Math.max(_,tt)-N;T.attr("viewBox",`${N} 0 ${B} ${D}`),pt(T,D,B,p.useMaxWidth)},"draw"),Lt={draw:Et},Gt={parser:At,db:V,renderer:Lt,styles:_t};export{Gt as diagram};
