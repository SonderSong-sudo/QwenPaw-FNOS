import{aV as ne,aU as ce,ba as oe,b9 as le,aW as ue,aX as de,aY as l,aZ as Q,a_ as mt,bo as fe,bp as he,bq as ke,b0 as me,br as ye,bs as ge,a$ as G,bt as ve,bu as Yt,bv as Bt,bw as pe,bx as Te,by as xe,bz as be,bA as we,bB as _e,bC as Ce,bD as zt,bE as qt,bF as Xt,bG as Ut,bH as jt,bI as De,b6 as Ee,b4 as Se,bb as Ie,bi as Ae}from"./ui-vendor-D67aqjKF.js";import{d as L,y as Fe,a as Le,b as Me,z as Oe}from"./utils-vendor-DW8wLLZl.js";import"./react-vendor-DAURSz_k.js";import"./markdown-vendor-zoJ7LKuz.js";var _t=(function(){var t=l(function(y,n,d,f){for(d=d||{},f=y.length;f--;d[y[f]]=n);return d},"o"),s=[6,8,10,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,33,35,36,38,40],i=[1,26],a=[1,27],r=[1,28],h=[1,29],m=[1,30],C=[1,31],M=[1,32],z=[1,33],S=[1,34],Y=[1,9],O=[1,10],N=[1,11],U=[1,12],W=[1,13],_=[1,14],it=[1,15],at=[1,16],rt=[1,19],nt=[1,20],K=[1,21],ct=[1,22],ot=[1,23],lt=[1,25],ut=[1,35],k={trace:l(function(){},"trace"),yy:{},symbols_:{error:2,start:3,gantt:4,document:5,EOF:6,line:7,SPACE:8,statement:9,NL:10,weekday:11,weekday_monday:12,weekday_tuesday:13,weekday_wednesday:14,weekday_thursday:15,weekday_friday:16,weekday_saturday:17,weekday_sunday:18,weekend:19,weekend_friday:20,weekend_saturday:21,dateFormat:22,inclusiveEndDates:23,topAxis:24,axisFormat:25,tickInterval:26,excludes:27,includes:28,todayMarker:29,title:30,acc_title:31,acc_title_value:32,acc_descr:33,acc_descr_value:34,acc_descr_multiline_value:35,section:36,clickStatement:37,taskTxt:38,taskData:39,click:40,callbackname:41,callbackargs:42,href:43,clickStatementDebug:44,$accept:0,$end:1},terminals_:{2:"error",4:"gantt",6:"EOF",8:"SPACE",10:"NL",12:"weekday_monday",13:"weekday_tuesday",14:"weekday_wednesday",15:"weekday_thursday",16:"weekday_friday",17:"weekday_saturday",18:"weekday_sunday",20:"weekend_friday",21:"weekend_saturday",22:"dateFormat",23:"inclusiveEndDates",24:"topAxis",25:"axisFormat",26:"tickInterval",27:"excludes",28:"includes",29:"todayMarker",30:"title",31:"acc_title",32:"acc_title_value",33:"acc_descr",34:"acc_descr_value",35:"acc_descr_multiline_value",36:"section",38:"taskTxt",39:"taskData",40:"click",41:"callbackname",42:"callbackargs",43:"href"},productions_:[0,[3,3],[5,0],[5,2],[7,2],[7,1],[7,1],[7,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[19,1],[19,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,2],[9,2],[9,1],[9,1],[9,1],[9,2],[37,2],[37,3],[37,3],[37,4],[37,3],[37,4],[37,2],[44,2],[44,3],[44,3],[44,4],[44,3],[44,4],[44,2]],performAction:l(function(n,d,f,u,b,e,x){var o=e.length-1;switch(b){case 1:return e[o-1];case 2:this.$=[];break;case 3:e[o-1].push(e[o]),this.$=e[o-1];break;case 4:case 5:this.$=e[o];break;case 6:case 7:this.$=[];break;case 8:u.setWeekday("monday");break;case 9:u.setWeekday("tuesday");break;case 10:u.setWeekday("wednesday");break;case 11:u.setWeekday("thursday");break;case 12:u.setWeekday("friday");break;case 13:u.setWeekday("saturday");break;case 14:u.setWeekday("sunday");break;case 15:u.setWeekend("friday");break;case 16:u.setWeekend("saturday");break;case 17:u.setDateFormat(e[o].substr(11)),this.$=e[o].substr(11);break;case 18:u.enableInclusiveEndDates(),this.$=e[o].substr(18);break;case 19:u.TopAxis(),this.$=e[o].substr(8);break;case 20:u.setAxisFormat(e[o].substr(11)),this.$=e[o].substr(11);break;case 21:u.setTickInterval(e[o].substr(13)),this.$=e[o].substr(13);break;case 22:u.setExcludes(e[o].substr(9)),this.$=e[o].substr(9);break;case 23:u.setIncludes(e[o].substr(9)),this.$=e[o].substr(9);break;case 24:u.setTodayMarker(e[o].substr(12)),this.$=e[o].substr(12);break;case 27:u.setDiagramTitle(e[o].substr(6)),this.$=e[o].substr(6);break;case 28:this.$=e[o].trim(),u.setAccTitle(this.$);break;case 29:case 30:this.$=e[o].trim(),u.setAccDescription(this.$);break;case 31:u.addSection(e[o].substr(8)),this.$=e[o].substr(8);break;case 33:u.addTask(e[o-1],e[o]),this.$="task";break;case 34:this.$=e[o-1],u.setClickEvent(e[o-1],e[o],null);break;case 35:this.$=e[o-2],u.setClickEvent(e[o-2],e[o-1],e[o]);break;case 36:this.$=e[o-2],u.setClickEvent(e[o-2],e[o-1],null),u.setLink(e[o-2],e[o]);break;case 37:this.$=e[o-3],u.setClickEvent(e[o-3],e[o-2],e[o-1]),u.setLink(e[o-3],e[o]);break;case 38:this.$=e[o-2],u.setClickEvent(e[o-2],e[o],null),u.setLink(e[o-2],e[o-1]);break;case 39:this.$=e[o-3],u.setClickEvent(e[o-3],e[o-1],e[o]),u.setLink(e[o-3],e[o-2]);break;case 40:this.$=e[o-1],u.setLink(e[o-1],e[o]);break;case 41:case 47:this.$=e[o-1]+" "+e[o];break;case 42:case 43:case 45:this.$=e[o-2]+" "+e[o-1]+" "+e[o];break;case 44:case 46:this.$=e[o-3]+" "+e[o-2]+" "+e[o-1]+" "+e[o];break}},"anonymous"),table:[{3:1,4:[1,2]},{1:[3]},t(s,[2,2],{5:3}),{6:[1,4],7:5,8:[1,6],9:7,10:[1,8],11:17,12:i,13:a,14:r,15:h,16:m,17:C,18:M,19:18,20:z,21:S,22:Y,23:O,24:N,25:U,26:W,27:_,28:it,29:at,30:rt,31:nt,33:K,35:ct,36:ot,37:24,38:lt,40:ut},t(s,[2,7],{1:[2,1]}),t(s,[2,3]),{9:36,11:17,12:i,13:a,14:r,15:h,16:m,17:C,18:M,19:18,20:z,21:S,22:Y,23:O,24:N,25:U,26:W,27:_,28:it,29:at,30:rt,31:nt,33:K,35:ct,36:ot,37:24,38:lt,40:ut},t(s,[2,5]),t(s,[2,6]),t(s,[2,17]),t(s,[2,18]),t(s,[2,19]),t(s,[2,20]),t(s,[2,21]),t(s,[2,22]),t(s,[2,23]),t(s,[2,24]),t(s,[2,25]),t(s,[2,26]),t(s,[2,27]),{32:[1,37]},{34:[1,38]},t(s,[2,30]),t(s,[2,31]),t(s,[2,32]),{39:[1,39]},t(s,[2,8]),t(s,[2,9]),t(s,[2,10]),t(s,[2,11]),t(s,[2,12]),t(s,[2,13]),t(s,[2,14]),t(s,[2,15]),t(s,[2,16]),{41:[1,40],43:[1,41]},t(s,[2,4]),t(s,[2,28]),t(s,[2,29]),t(s,[2,33]),t(s,[2,34],{42:[1,42],43:[1,43]}),t(s,[2,40],{41:[1,44]}),t(s,[2,35],{43:[1,45]}),t(s,[2,36]),t(s,[2,38],{42:[1,46]}),t(s,[2,37]),t(s,[2,39])],defaultActions:{},parseError:l(function(n,d){if(d.recoverable)this.trace(n);else{var f=new Error(n);throw f.hash=d,f}},"parseError"),parse:l(function(n){var d=this,f=[0],u=[],b=[null],e=[],x=this.table,o="",F=0,c=0,g=2,v=1,D=e.slice.call(arguments,1),p=Object.create(this.lexer),I={yy:{}};for(var E in this.yy)Object.prototype.hasOwnProperty.call(this.yy,E)&&(I.yy[E]=this.yy[E]);p.setInput(n,I.yy),I.yy.lexer=p,I.yy.parser=this,typeof p.yylloc>"u"&&(p.yylloc={});var dt=p.yylloc;e.push(dt);var Tt=p.options&&p.options.ranges;typeof I.yy.parseError=="function"?this.parseError=I.yy.parseError:this.parseError=Object.getPrototypeOf(this).parseError;function re(R){f.length=f.length-2*R,b.length=b.length-R,e.length=e.length-R}l(re,"popStack");function Pt(){var R;return R=u.pop()||p.lex()||v,typeof R!="number"&&(R instanceof Array&&(u=R,R=u.pop()),R=d.symbols_[R]||R),R}l(Pt,"lex");for(var V,j,P,xt,Z={},ht,q,Nt,kt;;){if(j=f[f.length-1],this.defaultActions[j]?P=this.defaultActions[j]:((V===null||typeof V>"u")&&(V=Pt()),P=x[j]&&x[j][V]),typeof P>"u"||!P.length||!P[0]){var bt="";kt=[];for(ht in x[j])this.terminals_[ht]&&ht>g&&kt.push("'"+this.terminals_[ht]+"'");p.showPosition?bt="Parse error on line "+(F+1)+`:
`+p.showPosition()+`
Expecting `+kt.join(", ")+", got '"+(this.terminals_[V]||V)+"'":bt="Parse error on line "+(F+1)+": Unexpected "+(V==v?"end of input":"'"+(this.terminals_[V]||V)+"'"),this.parseError(bt,{text:p.match,token:this.terminals_[V]||V,line:p.yylineno,loc:dt,expected:kt})}if(P[0]instanceof Array&&P.length>1)throw new Error("Parse Error: multiple actions possible at state: "+j+", token: "+V);switch(P[0]){case 1:f.push(V),b.push(p.yytext),e.push(p.yylloc),f.push(P[1]),V=null,c=p.yyleng,o=p.yytext,F=p.yylineno,dt=p.yylloc;break;case 2:if(q=this.productions_[P[1]][1],Z.$=b[b.length-q],Z._$={first_line:e[e.length-(q||1)].first_line,last_line:e[e.length-1].last_line,first_column:e[e.length-(q||1)].first_column,last_column:e[e.length-1].last_column},Tt&&(Z._$.range=[e[e.length-(q||1)].range[0],e[e.length-1].range[1]]),xt=this.performAction.apply(Z,[o,c,F,I.yy,P[1],b,e].concat(D)),typeof xt<"u")return xt;q&&(f=f.slice(0,-1*q*2),b=b.slice(0,-1*q),e=e.slice(0,-1*q)),f.push(this.productions_[P[1]][0]),b.push(Z.$),e.push(Z._$),Nt=x[f[f.length-2]][f[f.length-1]],f.push(Nt);break;case 3:return!0}}return!0},"parse")},w=(function(){var y={EOF:1,parseError:l(function(d,f){if(this.yy.parser)this.yy.parser.parseError(d,f);else throw new Error(d)},"parseError"),setInput:l(function(n,d){return this.yy=d||this.yy||{},this._input=n,this._more=this._backtrack=this.done=!1,this.yylineno=this.yyleng=0,this.yytext=this.matched=this.match="",this.conditionStack=["INITIAL"],this.yylloc={first_line:1,first_column:0,last_line:1,last_column:0},this.options.ranges&&(this.yylloc.range=[0,0]),this.offset=0,this},"setInput"),input:l(function(){var n=this._input[0];this.yytext+=n,this.yyleng++,this.offset++,this.match+=n,this.matched+=n;var d=n.match(/(?:\r\n?|\n).*/g);return d?(this.yylineno++,this.yylloc.last_line++):this.yylloc.last_column++,this.options.ranges&&this.yylloc.range[1]++,this._input=this._input.slice(1),n},"input"),unput:l(function(n){var d=n.length,f=n.split(/(?:\r\n?|\n)/g);this._input=n+this._input,this.yytext=this.yytext.substr(0,this.yytext.length-d),this.offset-=d;var u=this.match.split(/(?:\r\n?|\n)/g);this.match=this.match.substr(0,this.match.length-1),this.matched=this.matched.substr(0,this.matched.length-1),f.length-1&&(this.yylineno-=f.length-1);var b=this.yylloc.range;return this.yylloc={first_line:this.yylloc.first_line,last_line:this.yylineno+1,first_column:this.yylloc.first_column,last_column:f?(f.length===u.length?this.yylloc.first_column:0)+u[u.length-f.length].length-f[0].length:this.yylloc.first_column-d},this.options.ranges&&(this.yylloc.range=[b[0],b[0]+this.yyleng-d]),this.yyleng=this.yytext.length,this},"unput"),more:l(function(){return this._more=!0,this},"more"),reject:l(function(){if(this.options.backtrack_lexer)this._backtrack=!0;else return this.parseError("Lexical error on line "+(this.yylineno+1)+`. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).
`+this.showPosition(),{text:"",token:null,line:this.yylineno});return this},"reject"),less:l(function(n){this.unput(this.match.slice(n))},"less"),pastInput:l(function(){var n=this.matched.substr(0,this.matched.length-this.match.length);return(n.length>20?"...":"")+n.substr(-20).replace(/\n/g,"")},"pastInput"),upcomingInput:l(function(){var n=this.match;return n.length<20&&(n+=this._input.substr(0,20-n.length)),(n.substr(0,20)+(n.length>20?"...":"")).replace(/\n/g,"")},"upcomingInput"),showPosition:l(function(){var n=this.pastInput(),d=new Array(n.length+1).join("-");return n+this.upcomingInput()+`
`+d+"^"},"showPosition"),test_match:l(function(n,d){var f,u,b;if(this.options.backtrack_lexer&&(b={yylineno:this.yylineno,yylloc:{first_line:this.yylloc.first_line,last_line:this.last_line,first_column:this.yylloc.first_column,last_column:this.yylloc.last_column},yytext:this.yytext,match:this.match,matches:this.matches,matched:this.matched,yyleng:this.yyleng,offset:this.offset,_more:this._more,_input:this._input,yy:this.yy,conditionStack:this.conditionStack.slice(0),done:this.done},this.options.ranges&&(b.yylloc.range=this.yylloc.range.slice(0))),u=n[0].match(/(?:\r\n?|\n).*/g),u&&(this.yylineno+=u.length),this.yylloc={first_line:this.yylloc.last_line,last_line:this.yylineno+1,first_column:this.yylloc.last_column,last_column:u?u[u.length-1].length-u[u.length-1].match(/\r?\n?/)[0].length:this.yylloc.last_column+n[0].length},this.yytext+=n[0],this.match+=n[0],this.matches=n,this.yyleng=this.yytext.length,this.options.ranges&&(this.yylloc.range=[this.offset,this.offset+=this.yyleng]),this._more=!1,this._backtrack=!1,this._input=this._input.slice(n[0].length),this.matched+=n[0],f=this.performAction.call(this,this.yy,this,d,this.conditionStack[this.conditionStack.length-1]),this.done&&this._input&&(this.done=!1),f)return f;if(this._backtrack){for(var e in b)this[e]=b[e];return!1}return!1},"test_match"),next:l(function(){if(this.done)return this.EOF;this._input||(this.done=!0);var n,d,f,u;this._more||(this.yytext="",this.match="");for(var b=this._currentRules(),e=0;e<b.length;e++)if(f=this._input.match(this.rules[b[e]]),f&&(!d||f[0].length>d[0].length)){if(d=f,u=e,this.options.backtrack_lexer){if(n=this.test_match(f,b[e]),n!==!1)return n;if(this._backtrack){d=!1;continue}else return!1}else if(!this.options.flex)break}return d?(n=this.test_match(d,b[u]),n!==!1?n:!1):this._input===""?this.EOF:this.parseError("Lexical error on line "+(this.yylineno+1)+`. Unrecognized text.
`+this.showPosition(),{text:"",token:null,line:this.yylineno})},"next"),lex:l(function(){var d=this.next();return d||this.lex()},"lex"),begin:l(function(d){this.conditionStack.push(d)},"begin"),popState:l(function(){var d=this.conditionStack.length-1;return d>0?this.conditionStack.pop():this.conditionStack[0]},"popState"),_currentRules:l(function(){return this.conditionStack.length&&this.conditionStack[this.conditionStack.length-1]?this.conditions[this.conditionStack[this.conditionStack.length-1]].rules:this.conditions.INITIAL.rules},"_currentRules"),topState:l(function(d){return d=this.conditionStack.length-1-Math.abs(d||0),d>=0?this.conditionStack[d]:"INITIAL"},"topState"),pushState:l(function(d){this.begin(d)},"pushState"),stateStackSize:l(function(){return this.conditionStack.length},"stateStackSize"),options:{"case-insensitive":!0},performAction:l(function(d,f,u,b){switch(u){case 0:return this.begin("open_directive"),"open_directive";case 1:return this.begin("acc_title"),31;case 2:return this.popState(),"acc_title_value";case 3:return this.begin("acc_descr"),33;case 4:return this.popState(),"acc_descr_value";case 5:this.begin("acc_descr_multiline");break;case 6:this.popState();break;case 7:return"acc_descr_multiline_value";case 8:break;case 9:break;case 10:break;case 11:return 10;case 12:break;case 13:break;case 14:this.begin("href");break;case 15:this.popState();break;case 16:return 43;case 17:this.begin("callbackname");break;case 18:this.popState();break;case 19:this.popState(),this.begin("callbackargs");break;case 20:return 41;case 21:this.popState();break;case 22:return 42;case 23:this.begin("click");break;case 24:this.popState();break;case 25:return 40;case 26:return 4;case 27:return 22;case 28:return 23;case 29:return 24;case 30:return 25;case 31:return 26;case 32:return 28;case 33:return 27;case 34:return 29;case 35:return 12;case 36:return 13;case 37:return 14;case 38:return 15;case 39:return 16;case 40:return 17;case 41:return 18;case 42:return 20;case 43:return 21;case 44:return"date";case 45:return 30;case 46:return"accDescription";case 47:return 36;case 48:return 38;case 49:return 39;case 50:return":";case 51:return 6;case 52:return"INVALID"}},"anonymous"),rules:[/^(?:%%\{)/i,/^(?:accTitle\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*\{\s*)/i,/^(?:[\}])/i,/^(?:[^\}]*)/i,/^(?:%%(?!\{)*[^\n]*)/i,/^(?:[^\}]%%*[^\n]*)/i,/^(?:%%*[^\n]*[\n]*)/i,/^(?:[\n]+)/i,/^(?:\s+)/i,/^(?:%[^\n]*)/i,/^(?:href[\s]+["])/i,/^(?:["])/i,/^(?:[^"]*)/i,/^(?:call[\s]+)/i,/^(?:\([\s]*\))/i,/^(?:\()/i,/^(?:[^(]*)/i,/^(?:\))/i,/^(?:[^)]*)/i,/^(?:click[\s]+)/i,/^(?:[\s\n])/i,/^(?:[^\s\n]*)/i,/^(?:gantt\b)/i,/^(?:dateFormat\s[^#\n;]+)/i,/^(?:inclusiveEndDates\b)/i,/^(?:topAxis\b)/i,/^(?:axisFormat\s[^#\n;]+)/i,/^(?:tickInterval\s[^#\n;]+)/i,/^(?:includes\s[^#\n;]+)/i,/^(?:excludes\s[^#\n;]+)/i,/^(?:todayMarker\s[^\n;]+)/i,/^(?:weekday\s+monday\b)/i,/^(?:weekday\s+tuesday\b)/i,/^(?:weekday\s+wednesday\b)/i,/^(?:weekday\s+thursday\b)/i,/^(?:weekday\s+friday\b)/i,/^(?:weekday\s+saturday\b)/i,/^(?:weekday\s+sunday\b)/i,/^(?:weekend\s+friday\b)/i,/^(?:weekend\s+saturday\b)/i,/^(?:\d\d\d\d-\d\d-\d\d\b)/i,/^(?:title\s[^\n]+)/i,/^(?:accDescription\s[^#\n;]+)/i,/^(?:section\s[^\n]+)/i,/^(?:[^:\n]+)/i,/^(?::[^#\n;]+)/i,/^(?::)/i,/^(?:$)/i,/^(?:.)/i],conditions:{acc_descr_multiline:{rules:[6,7],inclusive:!1},acc_descr:{rules:[4],inclusive:!1},acc_title:{rules:[2],inclusive:!1},callbackargs:{rules:[21,22],inclusive:!1},callbackname:{rules:[18,19,20],inclusive:!1},href:{rules:[15,16],inclusive:!1},click:{rules:[24,25],inclusive:!1},INITIAL:{rules:[0,1,3,5,8,9,10,11,12,13,14,17,23,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52],inclusive:!0}}};return y})();k.lexer=w;function T(){this.yy={}}return l(T,"Parser"),T.prototype=k,k.Parser=T,new T})();_t.parser=_t;var Ve=_t;L.extend(Fe);L.extend(Le);L.extend(Me);var Gt={friday:5,saturday:6},B="",St="",It=void 0,At="",tt=[],et=[],Ft=new Map,Lt=[],vt=[],st="",Mt="",Zt=["active","done","crit","milestone","vert"],Ot=[],J="",ft=!1,Vt=!1,Rt="sunday",pt="saturday",Ct=0,Re=l(function(){Lt=[],vt=[],st="",Ot=[],yt=0,Et=void 0,gt=void 0,A=[],B="",St="",Mt="",It=void 0,At="",tt=[],et=[],ft=!1,Vt=!1,Ct=0,Ft=new Map,J="",Ie(),Rt="sunday",pt="saturday"},"clear"),We=l(function(t){J=t},"setDiagramId"),Pe=l(function(t){St=t},"setAxisFormat"),Ne=l(function(){return St},"getAxisFormat"),Ye=l(function(t){It=t},"setTickInterval"),Be=l(function(){return It},"getTickInterval"),ze=l(function(t){At=t},"setTodayMarker"),qe=l(function(){return At},"getTodayMarker"),Xe=l(function(t){B=t},"setDateFormat"),Ue=l(function(){ft=!0},"enableInclusiveEndDates"),je=l(function(){return ft},"endDatesAreInclusive"),Ge=l(function(){Vt=!0},"enableTopAxis"),He=l(function(){return Vt},"topAxisEnabled"),Ke=l(function(t){Mt=t},"setDisplayMode"),Ze=l(function(){return Mt},"getDisplayMode"),Je=l(function(){return B},"getDateFormat"),Jt=l((t,s)=>{const i=s.toLowerCase().split(/[\s,]+/).filter(a=>a!=="");return[...new Set([...t,...i])]},"mergeTokens"),Qe=l(function(t){tt=Jt(tt,t)},"setIncludes"),$e=l(function(){return tt},"getIncludes"),ts=l(function(t){et=Jt(et,t)},"setExcludes"),es=l(function(){return et},"getExcludes"),ss=l(function(){return Ft},"getLinks"),is=l(function(t){st=t,Lt.push(t)},"addSection"),as=l(function(){return Lt},"getSections"),rs=l(function(){let t=Ht();const s=10;let i=0;for(;!t&&i<s;)t=Ht(),i++;return vt=A,vt},"getTasks"),Qt=l(function(t,s,i,a){const r=t.format(s.trim()),h=t.format("YYYY-MM-DD");return a.includes(r)||a.includes(h)?!1:i.includes("weekends")&&(t.isoWeekday()===Gt[pt]||t.isoWeekday()===Gt[pt]+1)||i.includes(t.format("dddd").toLowerCase())?!0:i.includes(r)||i.includes(h)},"isInvalidDate"),ns=l(function(t){Rt=t},"setWeekday"),cs=l(function(){return Rt},"getWeekday"),os=l(function(t){pt=t},"setWeekend"),$t=l(function(t,s,i,a){if(!i.length||t.manualEndTime)return;let r;t.startTime instanceof Date?r=L(t.startTime):r=L(t.startTime,s,!0),r=r.add(1,"d");let h;t.endTime instanceof Date?h=L(t.endTime):h=L(t.endTime,s,!0);const[m,C]=ls(r,h,s,i,a);t.endTime=m.toDate(),t.renderEndTime=C},"checkTaskDates"),ls=l(function(t,s,i,a,r){let h=!1,m=null;const C=s.add(1e4,"d");for(;t<=s;){if(h||(m=s.toDate()),h=Qt(t,i,a,r),h&&(s=s.add(1,"d"),s>C))throw new Error("Failed to find a valid date that was not excluded by `excludes` after 10,000 iterations.");t=t.add(1,"d")}return[s,m]},"fixTaskDates"),Dt=l(function(t,s,i){if(i=i.trim(),l(C=>{const M=C.trim();return M==="x"||M==="X"},"isTimestampFormat")(s)&&/^\d+$/.test(i))return new Date(Number(i));const h=/^after\s+(?<ids>[\d\w- ]+)/.exec(i);if(h!==null){let C=null;for(const z of h.groups.ids.split(" ")){let S=H(z);S!==void 0&&(!C||S.endTime>C.endTime)&&(C=S)}if(C)return C.endTime;const M=new Date;return M.setHours(0,0,0,0),M}let m=L(i,s.trim(),!0);if(m.isValid())return m.toDate();{G.debug("Invalid date:"+i),G.debug("With date format:"+s.trim());const C=new Date(i);if(C===void 0||isNaN(C.getTime())||C.getFullYear()<-1e4||C.getFullYear()>1e4)throw new Error("Invalid date:"+i);return C}},"getStartDate"),te=l(function(t){const s=/^(\d+(?:\.\d+)?)([Mdhmswy]|ms)$/.exec(t.trim());return s!==null?[Number.parseFloat(s[1]),s[2]]:[NaN,"ms"]},"parseDuration"),ee=l(function(t,s,i,a=!1){i=i.trim();const h=/^until\s+(?<ids>[\d\w- ]+)/.exec(i);if(h!==null){let S=null;for(const O of h.groups.ids.split(" ")){let N=H(O);N!==void 0&&(!S||N.startTime<S.startTime)&&(S=N)}if(S)return S.startTime;const Y=new Date;return Y.setHours(0,0,0,0),Y}let m=L(i,s.trim(),!0);if(m.isValid())return a&&(m=m.add(1,"d")),m.toDate();let C=L(t);const[M,z]=te(i);if(!Number.isNaN(M)){const S=C.add(M,z);S.isValid()&&(C=S)}return C.toDate()},"getEndDate"),yt=0,$=l(function(t){return t===void 0?(yt=yt+1,"task"+yt):t},"parseId"),us=l(function(t,s){let i;s.substr(0,1)===":"?i=s.substr(1,s.length):i=s;const a=i.split(","),r={};Wt(a,r,Zt);for(let m=0;m<a.length;m++)a[m]=a[m].trim();let h="";switch(a.length){case 1:r.id=$(),r.startTime=t.endTime,h=a[0];break;case 2:r.id=$(),r.startTime=Dt(void 0,B,a[0]),h=a[1];break;case 3:r.id=$(a[0]),r.startTime=Dt(void 0,B,a[1]),h=a[2];break}return h&&(r.endTime=ee(r.startTime,B,h,ft),r.manualEndTime=L(h,"YYYY-MM-DD",!0).isValid(),$t(r,B,et,tt)),r},"compileData"),ds=l(function(t,s){let i;s.substr(0,1)===":"?i=s.substr(1,s.length):i=s;const a=i.split(","),r={};Wt(a,r,Zt);for(let h=0;h<a.length;h++)a[h]=a[h].trim();switch(a.length){case 1:r.id=$(),r.startTime={type:"prevTaskEnd",id:t},r.endTime={data:a[0]};break;case 2:r.id=$(),r.startTime={type:"getStartDate",startData:a[0]},r.endTime={data:a[1]};break;case 3:r.id=$(a[0]),r.startTime={type:"getStartDate",startData:a[1]},r.endTime={data:a[2]};break}return r},"parseData"),Et,gt,A=[],se={},fs=l(function(t,s){const i={section:st,type:st,processed:!1,manualEndTime:!1,renderEndTime:null,raw:{data:s},task:t,classes:[]},a=ds(gt,s);i.raw.startTime=a.startTime,i.raw.endTime=a.endTime,i.id=a.id,i.prevTaskId=gt,i.active=a.active,i.done=a.done,i.crit=a.crit,i.milestone=a.milestone,i.vert=a.vert,i.vert?i.order=-1:(i.order=Ct,Ct++);const r=A.push(i);gt=i.id,se[i.id]=r-1},"addTask"),H=l(function(t){const s=se[t];return A[s]},"findTaskById"),hs=l(function(t,s){const i={section:st,type:st,description:t,task:t,classes:[]},a=us(Et,s);i.startTime=a.startTime,i.endTime=a.endTime,i.id=a.id,i.active=a.active,i.done=a.done,i.crit=a.crit,i.milestone=a.milestone,i.vert=a.vert,Et=i,vt.push(i)},"addTaskOrg"),Ht=l(function(){const t=l(function(i){const a=A[i];let r="";switch(A[i].raw.startTime.type){case"prevTaskEnd":{const h=H(a.prevTaskId);a.startTime=h.endTime;break}case"getStartDate":r=Dt(void 0,B,A[i].raw.startTime.startData),r&&(A[i].startTime=r);break}return A[i].startTime&&(A[i].endTime=ee(A[i].startTime,B,A[i].raw.endTime.data,ft),A[i].endTime&&(A[i].processed=!0,A[i].manualEndTime=L(A[i].raw.endTime.data,"YYYY-MM-DD",!0).isValid(),$t(A[i],B,et,tt))),A[i].processed},"compileTask");let s=!0;for(const[i,a]of A.entries())t(i),s=s&&a.processed;return s},"compileTasks"),ks=l(function(t,s){let i=s;Q().securityLevel!=="loose"&&(i=Se.sanitizeUrl(s)),t.split(",").forEach(function(a){H(a)!==void 0&&(ae(a,()=>{window.open(i,"_self")}),Ft.set(a,i))}),ie(t,"clickable")},"setLink"),ie=l(function(t,s){t.split(",").forEach(function(i){let a=H(i);a!==void 0&&a.classes.push(s)})},"setClass"),ms=l(function(t,s,i){if(Q().securityLevel!=="loose"||s===void 0)return;let a=[];if(typeof i=="string"){a=i.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);for(let h=0;h<a.length;h++){let m=a[h].trim();m.startsWith('"')&&m.endsWith('"')&&(m=m.substr(1,m.length-2)),a[h]=m}}a.length===0&&a.push(t),H(t)!==void 0&&ae(t,()=>{Ae.runFunc(s,...a)})},"setClickFun"),ae=l(function(t,s){Ot.push(function(){const i=J?`${J}-${t}`:t,a=document.querySelector(`[id="${i}"]`);a!==null&&a.addEventListener("click",function(){s()})},function(){const i=J?`${J}-${t}`:t,a=document.querySelector(`[id="${i}-text"]`);a!==null&&a.addEventListener("click",function(){s()})})},"pushFun"),ys=l(function(t,s,i){t.split(",").forEach(function(a){ms(a,s,i)}),ie(t,"clickable")},"setClickEvent"),gs=l(function(t){Ot.forEach(function(s){s(t)})},"bindFunctions"),vs={getConfig:l(()=>Q().gantt,"getConfig"),clear:Re,setDateFormat:Xe,getDateFormat:Je,enableInclusiveEndDates:Ue,endDatesAreInclusive:je,enableTopAxis:Ge,topAxisEnabled:He,setAxisFormat:Pe,getAxisFormat:Ne,setTickInterval:Ye,getTickInterval:Be,setTodayMarker:ze,getTodayMarker:qe,setAccTitle:de,getAccTitle:ue,setDiagramTitle:le,getDiagramTitle:oe,setDiagramId:We,setDisplayMode:Ke,getDisplayMode:Ze,setAccDescription:ce,getAccDescription:ne,addSection:is,getSections:as,getTasks:rs,addTask:fs,findTaskById:H,addTaskOrg:hs,setIncludes:Qe,getIncludes:$e,setExcludes:ts,getExcludes:es,setClickEvent:ys,setLink:ks,getLinks:ss,bindFunctions:gs,parseDuration:te,isInvalidDate:Qt,setWeekday:ns,getWeekday:cs,setWeekend:os};function Wt(t,s,i){let a=!0;for(;a;)a=!1,i.forEach(function(r){const h="^\\s*"+r+"\\s*$",m=new RegExp(h);t[0].match(m)&&(s[r]=!0,t.shift(1),a=!0)})}l(Wt,"getTaskTags");L.extend(Oe);var ps=l(function(){G.debug("Something is calling, setConf, remove the call")},"setConf"),Kt={monday:Ce,tuesday:_e,wednesday:we,thursday:be,friday:xe,saturday:Te,sunday:pe},Ts=l((t,s)=>{let i=[...t].map(()=>-1/0),a=[...t].sort((h,m)=>h.startTime-m.startTime||h.order-m.order),r=0;for(const h of a)for(let m=0;m<i.length;m++)if(h.startTime>=i[m]){i[m]=h.endTime,h.order=m+s,m>r&&(r=m);break}return r},"getMaxIntersections"),X,wt=1e4,xs=l(function(t,s,i,a){const r=Q().gantt;a.db.setDiagramId(s);const h=Q().securityLevel;let m;h==="sandbox"&&(m=mt("#i"+s));const C=h==="sandbox"?mt(m.nodes()[0].contentDocument.body):mt("body"),M=h==="sandbox"?m.nodes()[0].contentDocument:document,z=M.getElementById(s);X=z.parentElement.offsetWidth,X===void 0&&(X=1200),r.useWidth!==void 0&&(X=r.useWidth);const S=a.db.getTasks(),Y=S.filter(k=>!k.vert);let O=[];for(const k of Y)O.push(k.type);O=ut(O);const N={};let U=2*r.topPadding;if(a.db.getDisplayMode()==="compact"||r.displayMode==="compact"){const k={};for(const T of Y)k[T.section]===void 0?k[T.section]=[T]:k[T.section].push(T);let w=0;for(const T of Object.keys(k)){const y=Ts(k[T],w)+1;w+=y,U+=y*(r.barHeight+r.barGap),N[T]=y}}else{U+=Y.length*(r.barHeight+r.barGap);for(const k of O)N[k]=Y.filter(w=>w.type===k).length}z.setAttribute("viewBox","0 0 "+X+" "+U);const W=C.select(`[id="${s}"]`),_=fe().domain([he(S,function(k){return k.startTime}),ke(S,function(k){return k.endTime})]).rangeRound([0,X-r.leftPadding-r.rightPadding]);function it(k,w){const T=k.startTime,y=w.startTime;let n=0;return T>y?n=1:T<y&&(n=-1),n}l(it,"taskCompare"),S.sort(it),at(S,X,U),me(W,U,X,r.useMaxWidth),W.append("text").text(a.db.getDiagramTitle()).attr("x",X/2).attr("y",r.titleTopMargin).attr("class","titleText");function at(k,w,T){const y=r.barHeight,n=y+r.barGap,d=r.topPadding,f=r.leftPadding,u=ye().domain([0,O.length]).range(["#00B9FA","#F95002"]).interpolate(ge);nt(n,d,f,w,T,k,a.db.getExcludes(),a.db.getIncludes()),ct(f,d,w,T),rt(k,n,d,f,y,u,w),ot(n,d),lt(f,d,w,T)}l(at,"makeGantt");function rt(k,w,T,y,n,d,f){k.sort((c,g)=>c.vert===g.vert?0:c.vert?1:-1);const u=k.filter(c=>!c.vert),e=[...new Set(u.map(c=>c.order))].map(c=>u.find(g=>g.order===c));W.append("g").selectAll("rect").data(e).enter().append("rect").attr("x",0).attr("y",function(c,g){return g=c.order,g*w+T-2}).attr("width",function(){return f-r.rightPadding/2}).attr("height",w).attr("class",function(c){for(const[g,v]of O.entries())if(c.type===v)return"section section"+g%r.numberSectionStyles;return"section section0"}).enter();const x=W.append("g").selectAll("rect").data(k).enter(),o=a.db.getLinks();if(x.append("rect").attr("id",function(c){return s+"-"+c.id}).attr("rx",3).attr("ry",3).attr("x",function(c){return c.milestone?_(c.startTime)+y+.5*(_(c.endTime)-_(c.startTime))-.5*n:_(c.startTime)+y}).attr("y",function(c,g){return g=c.order,c.vert?r.gridLineStartPadding:g*w+T}).attr("width",function(c){return c.milestone?n:c.vert?.08*n:_(c.renderEndTime||c.endTime)-_(c.startTime)}).attr("height",function(c){return c.vert?u.length*(r.barHeight+r.barGap)+r.barHeight*2:n}).attr("transform-origin",function(c,g){return g=c.order,(_(c.startTime)+y+.5*(_(c.endTime)-_(c.startTime))).toString()+"px "+(g*w+T+.5*n).toString()+"px"}).attr("class",function(c){const g="task";let v="";c.classes.length>0&&(v=c.classes.join(" "));let D=0;for(const[I,E]of O.entries())c.type===E&&(D=I%r.numberSectionStyles);let p="";return c.active?c.crit?p+=" activeCrit":p=" active":c.done?c.crit?p=" doneCrit":p=" done":c.crit&&(p+=" crit"),p.length===0&&(p=" task"),c.milestone&&(p=" milestone "+p),c.vert&&(p=" vert "+p),p+=D,p+=" "+v,g+p}),x.append("text").attr("id",function(c){return s+"-"+c.id+"-text"}).text(function(c){return c.task}).attr("font-size",r.fontSize).attr("x",function(c){let g=_(c.startTime),v=_(c.renderEndTime||c.endTime);if(c.milestone&&(g+=.5*(_(c.endTime)-_(c.startTime))-.5*n,v=g+n),c.vert)return _(c.startTime)+y;const D=this.getBBox().width;return D>v-g?v+D+1.5*r.leftPadding>f?g+y-5:v+y+5:(v-g)/2+g+y}).attr("y",function(c,g){return c.vert?r.gridLineStartPadding+u.length*(r.barHeight+r.barGap)+60:(g=c.order,g*w+r.barHeight/2+(r.fontSize/2-2)+T)}).attr("text-height",n).attr("class",function(c){const g=_(c.startTime);let v=_(c.endTime);c.milestone&&(v=g+n);const D=this.getBBox().width;let p="";c.classes.length>0&&(p=c.classes.join(" "));let I=0;for(const[dt,Tt]of O.entries())c.type===Tt&&(I=dt%r.numberSectionStyles);let E="";return c.active&&(c.crit?E="activeCritText"+I:E="activeText"+I),c.done?c.crit?E=E+" doneCritText"+I:E=E+" doneText"+I:c.crit&&(E=E+" critText"+I),c.milestone&&(E+=" milestoneText"),c.vert&&(E+=" vertText"),D>v-g?v+D+1.5*r.leftPadding>f?p+" taskTextOutsideLeft taskTextOutside"+I+" "+E:p+" taskTextOutsideRight taskTextOutside"+I+" "+E+" width-"+D:p+" taskText taskText"+I+" "+E+" width-"+D}),Q().securityLevel==="sandbox"){let c;c=mt("#i"+s);const g=c.nodes()[0].contentDocument;x.filter(function(v){return o.has(v.id)}).each(function(v){var D=g.querySelector("#"+CSS.escape(s+"-"+v.id)),p=g.querySelector("#"+CSS.escape(s+"-"+v.id+"-text"));const I=D.parentNode;var E=g.createElement("a");E.setAttribute("xlink:href",o.get(v.id)),E.setAttribute("target","_top"),I.appendChild(E),E.appendChild(D),E.appendChild(p)})}}l(rt,"drawRects");function nt(k,w,T,y,n,d,f,u){if(f.length===0&&u.length===0)return;let b,e;for(const{startTime:v,endTime:D}of d)(b===void 0||v<b)&&(b=v),(e===void 0||D>e)&&(e=D);if(!b||!e)return;if(L(e).diff(L(b),"year")>5){G.warn("The difference between the min and max time is more than 5 years. This will cause performance issues. Skipping drawing exclude days.");return}const x=a.db.getDateFormat(),o=[];let F=null,c=L(b);for(;c.valueOf()<=e;)a.db.isInvalidDate(c,x,f,u)?F?F.end=c:F={start:c,end:c}:F&&(o.push(F),F=null),c=c.add(1,"d");W.append("g").selectAll("rect").data(o).enter().append("rect").attr("id",v=>s+"-exclude-"+v.start.format("YYYY-MM-DD")).attr("x",v=>_(v.start.startOf("day"))+T).attr("y",r.gridLineStartPadding).attr("width",v=>_(v.end.endOf("day"))-_(v.start.startOf("day"))).attr("height",n-w-r.gridLineStartPadding).attr("transform-origin",function(v,D){return(_(v.start)+T+.5*(_(v.end)-_(v.start))).toString()+"px "+(D*k+.5*n).toString()+"px"}).attr("class","exclude-range")}l(nt,"drawExcludeDays");function K(k,w,T,y){if(T<=0||k>w)return 1/0;const n=w-k,d=L.duration({[y??"day"]:T}).asMilliseconds();return d<=0?1/0:Math.ceil(n/d)}l(K,"getEstimatedTickCount");function ct(k,w,T,y){const n=a.db.getDateFormat(),d=a.db.getAxisFormat();let f;d?f=d:n==="D"?f="%d":f=r.axisFormat??"%Y-%m-%d";let u=ve(_).tickSize(-y+w+r.gridLineStartPadding).tickFormat(Yt(f));const e=/^([1-9]\d*)(millisecond|second|minute|hour|day|week|month)$/.exec(a.db.getTickInterval()||r.tickInterval);if(e!==null){const x=parseInt(e[1],10);if(isNaN(x)||x<=0)G.warn(`Invalid tick interval value: "${e[1]}". Skipping custom tick interval.`);else{const o=e[2],F=a.db.getWeekday()||r.weekday,c=_.domain(),g=c[0],v=c[1],D=K(g,v,x,o);if(D>wt)G.warn(`The tick interval "${x}${o}" would generate ${D} ticks, which exceeds the maximum allowed (${wt}). This may indicate an invalid date or time range. Skipping custom tick interval.`);else switch(o){case"millisecond":u.ticks(jt.every(x));break;case"second":u.ticks(Ut.every(x));break;case"minute":u.ticks(Xt.every(x));break;case"hour":u.ticks(qt.every(x));break;case"day":u.ticks(zt.every(x));break;case"week":u.ticks(Kt[F].every(x));break;case"month":u.ticks(Bt.every(x));break}}}if(W.append("g").attr("class","grid").attr("transform","translate("+k+", "+(y-50)+")").call(u).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10).attr("dy","1em"),a.db.topAxisEnabled()||r.topAxis){let x=De(_).tickSize(-y+w+r.gridLineStartPadding).tickFormat(Yt(f));if(e!==null){const o=parseInt(e[1],10);if(isNaN(o)||o<=0)G.warn(`Invalid tick interval value: "${e[1]}". Skipping custom tick interval.`);else{const F=e[2],c=a.db.getWeekday()||r.weekday,g=_.domain(),v=g[0],D=g[1];if(K(v,D,o,F)<=wt)switch(F){case"millisecond":x.ticks(jt.every(o));break;case"second":x.ticks(Ut.every(o));break;case"minute":x.ticks(Xt.every(o));break;case"hour":x.ticks(qt.every(o));break;case"day":x.ticks(zt.every(o));break;case"week":x.ticks(Kt[c].every(o));break;case"month":x.ticks(Bt.every(o));break}}}W.append("g").attr("class","grid").attr("transform","translate("+k+", "+w+")").call(x).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10)}}l(ct,"makeGrid");function ot(k,w){let T=0;const y=Object.keys(N).map(n=>[n,N[n]]);W.append("g").selectAll("text").data(y).enter().append(function(n){const d=n[0].split(Ee.lineBreakRegex),f=-(d.length-1)/2,u=M.createElementNS("http://www.w3.org/2000/svg","text");u.setAttribute("dy",f+"em");for(const[b,e]of d.entries()){const x=M.createElementNS("http://www.w3.org/2000/svg","tspan");x.setAttribute("alignment-baseline","central"),x.setAttribute("x","10"),b>0&&x.setAttribute("dy","1em"),x.textContent=e,u.appendChild(x)}return u}).attr("x",10).attr("y",function(n,d){if(d>0)for(let f=0;f<d;f++)return T+=y[d-1][1],n[1]*k/2+T*k+w;else return n[1]*k/2+w}).attr("font-size",r.sectionFontSize).attr("class",function(n){for(const[d,f]of O.entries())if(n[0]===f)return"sectionTitle sectionTitle"+d%r.numberSectionStyles;return"sectionTitle"})}l(ot,"vertLabels");function lt(k,w,T,y){const n=a.db.getTodayMarker();if(n==="off")return;const d=W.append("g").attr("class","today"),f=new Date,u=d.append("line");u.attr("x1",_(f)+k).attr("x2",_(f)+k).attr("y1",r.titleTopMargin).attr("y2",y-r.titleTopMargin).attr("class","today"),n!==""&&u.attr("style",n.replace(/,/g,";"))}l(lt,"drawToday");function ut(k){const w={},T=[];for(let y=0,n=k.length;y<n;++y)Object.prototype.hasOwnProperty.call(w,k[y])||(w[k[y]]=!0,T.push(k[y]));return T}l(ut,"checkUnique")},"draw"),bs={setConf:ps,draw:xs},ws=l(t=>`
  .mermaid-main-font {
        font-family: ${t.fontFamily};
  }

  .exclude-range {
    fill: ${t.excludeBkgColor};
  }

  .section {
    stroke: none;
    opacity: 0.2;
  }

  .section0 {
    fill: ${t.sectionBkgColor};
  }

  .section2 {
    fill: ${t.sectionBkgColor2};
  }

  .section1,
  .section3 {
    fill: ${t.altSectionBkgColor};
    opacity: 0.2;
  }

  .sectionTitle0 {
    fill: ${t.titleColor};
  }

  .sectionTitle1 {
    fill: ${t.titleColor};
  }

  .sectionTitle2 {
    fill: ${t.titleColor};
  }

  .sectionTitle3 {
    fill: ${t.titleColor};
  }

  .sectionTitle {
    text-anchor: start;
    font-family: ${t.fontFamily};
  }


  /* Grid and axis */

  .grid .tick {
    stroke: ${t.gridColor};
    opacity: 0.8;
    shape-rendering: crispEdges;
  }

  .grid .tick text {
    font-family: ${t.fontFamily};
    fill: ${t.textColor};
  }

  .grid path {
    stroke-width: 0;
  }


  /* Today line */

  .today {
    fill: none;
    stroke: ${t.todayLineColor};
    stroke-width: 2px;
  }


  /* Task styling */

  /* Default task */

  .task {
    stroke-width: 2;
  }

  .taskText {
    text-anchor: middle;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideRight {
    fill: ${t.taskTextDarkColor};
    text-anchor: start;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideLeft {
    fill: ${t.taskTextDarkColor};
    text-anchor: end;
  }


  /* Special case clickable */

  .task.clickable {
    cursor: pointer;
  }

  .taskText.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideLeft.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideRight.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }


  /* Specific task settings for the sections*/

  .taskText0,
  .taskText1,
  .taskText2,
  .taskText3 {
    fill: ${t.taskTextColor};
  }

  .task0,
  .task1,
  .task2,
  .task3 {
    fill: ${t.taskBkgColor};
    stroke: ${t.taskBorderColor};
  }

  .taskTextOutside0,
  .taskTextOutside2
  {
    fill: ${t.taskTextOutsideColor};
  }

  .taskTextOutside1,
  .taskTextOutside3 {
    fill: ${t.taskTextOutsideColor};
  }


  /* Active task */

  .active0,
  .active1,
  .active2,
  .active3 {
    fill: ${t.activeTaskBkgColor};
    stroke: ${t.activeTaskBorderColor};
  }

  .activeText0,
  .activeText1,
  .activeText2,
  .activeText3 {
    fill: ${t.taskTextDarkColor} !important;
  }


  /* Completed task */

  .done0,
  .done1,
  .done2,
  .done3 {
    stroke: ${t.doneTaskBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
  }

  .doneText0,
  .doneText1,
  .doneText2,
  .doneText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  /* Done task text displayed outside the bar sits against the diagram background,
     not against the done-task bar, so it must use the outside/contrast color. */
  .doneText0.taskTextOutsideLeft,
  .doneText0.taskTextOutsideRight,
  .doneText1.taskTextOutsideLeft,
  .doneText1.taskTextOutsideRight,
  .doneText2.taskTextOutsideLeft,
  .doneText2.taskTextOutsideRight,
  .doneText3.taskTextOutsideLeft,
  .doneText3.taskTextOutsideRight {
    fill: ${t.taskTextOutsideColor} !important;
  }


  /* Tasks on the critical line */

  .crit0,
  .crit1,
  .crit2,
  .crit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.critBkgColor};
    stroke-width: 2;
  }

  .activeCrit0,
  .activeCrit1,
  .activeCrit2,
  .activeCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.activeTaskBkgColor};
    stroke-width: 2;
  }

  .doneCrit0,
  .doneCrit1,
  .doneCrit2,
  .doneCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
    cursor: pointer;
    shape-rendering: crispEdges;
  }

  .milestone {
    transform: rotate(45deg) scale(0.8,0.8);
  }

  .milestoneText {
    font-style: italic;
  }
  .doneCritText0,
  .doneCritText1,
  .doneCritText2,
  .doneCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  /* Done-crit task text outside the bar — same reasoning as doneText above. */
  .doneCritText0.taskTextOutsideLeft,
  .doneCritText0.taskTextOutsideRight,
  .doneCritText1.taskTextOutsideLeft,
  .doneCritText1.taskTextOutsideRight,
  .doneCritText2.taskTextOutsideLeft,
  .doneCritText2.taskTextOutsideRight,
  .doneCritText3.taskTextOutsideLeft,
  .doneCritText3.taskTextOutsideRight {
    fill: ${t.taskTextOutsideColor} !important;
  }

  .vert {
    stroke: ${t.vertLineColor};
  }

  .vertText {
    font-size: 15px;
    text-anchor: middle;
    fill: ${t.vertLineColor} !important;
  }

  .activeCritText0,
  .activeCritText1,
  .activeCritText2,
  .activeCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  .titleText {
    text-anchor: middle;
    font-size: 18px;
    fill: ${t.titleColor||t.textColor};
    font-family: ${t.fontFamily};
  }
`,"getStyles"),_s=ws,Is={parser:Ve,db:vs,renderer:bs,styles:_s};export{Is as diagram};
