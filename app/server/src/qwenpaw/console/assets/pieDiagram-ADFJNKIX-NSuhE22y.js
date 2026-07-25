import{aK as U,aJ as H,aL as J,aM as K,b3 as Q,b2 as V,aN as s,aQ as w,aO as Z,be as j,bD as q,bF as X,bG as G,bH as Y,aR as ee,b8 as te,bI as ae,bf as re}from"./ui-vendor-B9FBKUHL.js";import{p as ie}from"./chunk-4BX2VUAB-DnebKz4e.js";import{p as se}from"./treemap-GDKQZRPO-CYcDdYwI.js";import"./react-vendor-C6b7ei06.js";import"./utils-vendor-boo87mIs.js";import"./markdown-vendor-CqKm7FZ7.js";var le=re.pie,D={sections:new Map,showData:!1},g=D.sections,C=D.showData,oe=structuredClone(le),ne=s(()=>structuredClone(oe),"getConfig"),ce=s(()=>{g=new Map,C=D.showData,te()},"clear"),pe=s(({label:e,value:a})=>{if(a<0)throw new Error(`"${e}" has invalid value: ${a}. Negative values are not allowed in pie charts. All slice values must be >= 0.`);g.has(e)||(g.set(e,a),w.debug(`added new section: ${e}, with value: ${a}`))},"addSection"),de=s(()=>g,"getSections"),ge=s(e=>{C=e},"setShowData"),ue=s(()=>C,"getShowData"),M={getConfig:ne,clear:ce,setDiagramTitle:V,getDiagramTitle:Q,setAccTitle:K,getAccTitle:J,setAccDescription:H,getAccDescription:U,addSection:pe,getSections:de,setShowData:ge,getShowData:ue},fe=s((e,a)=>{ie(e,a),a.setShowData(e.showData),e.sections.map(a.addSection)},"populateDb"),he={parse:s(async e=>{const a=await se("pie",e);w.debug(a),fe(a,M)},"parse")},me=s(e=>`
  .pieCircle{
    stroke: ${e.pieStrokeColor};
    stroke-width : ${e.pieStrokeWidth};
    opacity : ${e.pieOpacity};
  }
  .pieOuterCircle{
    stroke: ${e.pieOuterStrokeColor};
    stroke-width: ${e.pieOuterStrokeWidth};
    fill: none;
  }
  .pieTitleText {
    text-anchor: middle;
    font-size: ${e.pieTitleTextSize};
    fill: ${e.pieTitleTextColor};
    font-family: ${e.fontFamily};
  }
  .slice {
    font-family: ${e.fontFamily};
    fill: ${e.pieSectionTextColor};
    font-size:${e.pieSectionTextSize};
    // fill: white;
  }
  .legend text {
    fill: ${e.pieLegendTextColor};
    font-family: ${e.fontFamily};
    font-size: ${e.pieLegendTextSize};
  }
`,"getStyles"),ve=me,Se=s(e=>{const a=[...e.values()].reduce((r,l)=>r+l,0),b=[...e.entries()].map(([r,l])=>({label:r,value:l})).filter(r=>r.value/a*100>=1).sort((r,l)=>l.value-r.value);return ae().value(r=>r.value)(b)},"createPieArcs"),xe=s((e,a,b,$)=>{w.debug(`rendering pie chart
`+e);const r=$.db,l=Z(),y=j(r.getConfig(),l.pie),T=40,o=18,p=4,c=450,u=c,f=q(a),n=f.append("g");n.attr("transform","translate("+u/2+","+c/2+")");const{themeVariables:i}=l;let[A]=X(i.pieOuterStrokeWidth);A??(A=2);const E=y.textPosition,d=Math.min(u,c)/2-T,O=G().innerRadius(0).outerRadius(d),R=G().innerRadius(d*E).outerRadius(d*E);n.append("circle").attr("cx",0).attr("cy",0).attr("r",d+A/2).attr("class","pieOuterCircle");const h=r.getSections(),W=Se(h),I=[i.pie1,i.pie2,i.pie3,i.pie4,i.pie5,i.pie6,i.pie7,i.pie8,i.pie9,i.pie10,i.pie11,i.pie12];let m=0;h.forEach(t=>{m+=t});const _=W.filter(t=>(t.data.value/m*100).toFixed(0)!=="0"),v=Y(I);n.selectAll("mySlices").data(_).enter().append("path").attr("d",O).attr("fill",t=>v(t.data.label)).attr("class","pieCircle"),n.selectAll("mySlices").data(_).enter().append("text").text(t=>(t.data.value/m*100).toFixed(0)+"%").attr("transform",t=>"translate("+R.centroid(t)+")").style("text-anchor","middle").attr("class","slice"),n.append("text").text(r.getDiagramTitle()).attr("x",0).attr("y",-400/2).attr("class","pieTitleText");const k=[...h.entries()].map(([t,x])=>({label:t,value:x})),S=n.selectAll(".legend").data(k).enter().append("g").attr("class","legend").attr("transform",(t,x)=>{const z=o+p,N=z*k.length/2,P=12*o,B=x*z-N;return"translate("+P+","+B+")"});S.append("rect").attr("width",o).attr("height",o).style("fill",t=>v(t.label)).style("stroke",t=>v(t.label)),S.append("text").attr("x",o+p).attr("y",o-p).text(t=>r.getShowData()?`${t.label} [${t.value}]`:t.label);const L=Math.max(...S.selectAll("text").nodes().map(t=>(t==null?void 0:t.getBoundingClientRect().width)??0)),F=u+T+o+p+L;f.attr("viewBox",`0 0 ${F} ${c}`),ee(f,c,F,y.useMaxWidth)},"draw"),we={draw:xe},Ae={parser:he,db:M,renderer:we,styles:ve};export{Ae as diagram};
