import{e as sn,f as W,p as ln,a9 as fn,aG as Xt}from"#entry";function cn(t,e,n){return(e=dn(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Kt(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);e&&(a=a.filter(function(r){return Object.getOwnPropertyDescriptor(t,r).enumerable})),n.push.apply(n,a)}return n}function l(t){for(var e=1;e<arguments.length;e++){var n=arguments[e]!=null?arguments[e]:{};e%2?Kt(Object(n),!0).forEach(function(a){cn(t,a,n[a])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):Kt(Object(n)).forEach(function(a){Object.defineProperty(t,a,Object.getOwnPropertyDescriptor(n,a))})}return t}function un(t,e){if(typeof t!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var a=n.call(t,e);if(typeof a!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}function dn(t){var e=un(t,"string");return typeof e=="symbol"?e:e+""}const Vt=()=>{};let zt={},Oe={},Se=null,Pe={mark:Vt,measure:Vt};try{typeof window<"u"&&(zt=window),typeof document<"u"&&(Oe=document),typeof MutationObserver<"u"&&(Se=MutationObserver),typeof performance<"u"&&(Pe=performance)}catch{}const{userAgent:qt=""}=zt.navigator||{},L=zt,y=Oe,Qt=Se,et=Pe;L.document;const F=!!y.documentElement&&!!y.head&&typeof y.addEventListener=="function"&&typeof y.createElement=="function",ke=~qt.indexOf("MSIE")||~qt.indexOf("Trident/");var mn=/fa(s|r|l|t|d|dr|dl|dt|b|k|kd|ss|sr|sl|st|sds|sdr|sdl|sdt)?[\-\ ]/,gn=/Font ?Awesome ?([56 ]*)(Solid|Regular|Light|Thin|Duotone|Brands|Free|Pro|Sharp Duotone|Sharp|Kit)?.*/i,Ee={classic:{fa:"solid",fas:"solid","fa-solid":"solid",far:"regular","fa-regular":"regular",fal:"light","fa-light":"light",fat:"thin","fa-thin":"thin",fab:"brands","fa-brands":"brands"},duotone:{fa:"solid",fad:"solid","fa-solid":"solid","fa-duotone":"solid",fadr:"regular","fa-regular":"regular",fadl:"light","fa-light":"light",fadt:"thin","fa-thin":"thin"},sharp:{fa:"solid",fass:"solid","fa-solid":"solid",fasr:"regular","fa-regular":"regular",fasl:"light","fa-light":"light",fast:"thin","fa-thin":"thin"},"sharp-duotone":{fa:"solid",fasds:"solid","fa-solid":"solid",fasdr:"regular","fa-regular":"regular",fasdl:"light","fa-light":"light",fasdt:"thin","fa-thin":"thin"}},pn={GROUP:"duotone-group",PRIMARY:"primary",SECONDARY:"secondary"},Ie=["fa-classic","fa-duotone","fa-sharp","fa-sharp-duotone"],A="classic",lt="duotone",hn="sharp",yn="sharp-duotone",Ce=[A,lt,hn,yn],bn={classic:{900:"fas",400:"far",normal:"far",300:"fal",100:"fat"},duotone:{900:"fad",400:"fadr",300:"fadl",100:"fadt"},sharp:{900:"fass",400:"fasr",300:"fasl",100:"fast"},"sharp-duotone":{900:"fasds",400:"fasdr",300:"fasdl",100:"fasdt"}},vn={"Font Awesome 6 Free":{900:"fas",400:"far"},"Font Awesome 6 Pro":{900:"fas",400:"far",normal:"far",300:"fal",100:"fat"},"Font Awesome 6 Brands":{400:"fab",normal:"fab"},"Font Awesome 6 Duotone":{900:"fad",400:"fadr",normal:"fadr",300:"fadl",100:"fadt"},"Font Awesome 6 Sharp":{900:"fass",400:"fasr",normal:"fasr",300:"fasl",100:"fast"},"Font Awesome 6 Sharp Duotone":{900:"fasds",400:"fasdr",normal:"fasdr",300:"fasdl",100:"fasdt"}},xn=new Map([["classic",{defaultShortPrefixId:"fas",defaultStyleId:"solid",styleIds:["solid","regular","light","thin","brands"],futureStyleIds:[],defaultFontWeight:900}],["sharp",{defaultShortPrefixId:"fass",defaultStyleId:"solid",styleIds:["solid","regular","light","thin"],futureStyleIds:[],defaultFontWeight:900}],["duotone",{defaultShortPrefixId:"fad",defaultStyleId:"solid",styleIds:["solid","regular","light","thin"],futureStyleIds:[],defaultFontWeight:900}],["sharp-duotone",{defaultShortPrefixId:"fasds",defaultStyleId:"solid",styleIds:["solid","regular","light","thin"],futureStyleIds:[],defaultFontWeight:900}]]),An={classic:{solid:"fas",regular:"far",light:"fal",thin:"fat",brands:"fab"},duotone:{solid:"fad",regular:"fadr",light:"fadl",thin:"fadt"},sharp:{solid:"fass",regular:"fasr",light:"fasl",thin:"fast"},"sharp-duotone":{solid:"fasds",regular:"fasdr",light:"fasdl",thin:"fasdt"}},wn=["fak","fa-kit","fakd","fa-kit-duotone"],Zt={kit:{fak:"kit","fa-kit":"kit"},"kit-duotone":{fakd:"kit-duotone","fa-kit-duotone":"kit-duotone"}},On=["kit"],Sn={kit:{"fa-kit":"fak"}},Pn=["fak","fakd"],kn={kit:{fak:"fa-kit"}},Jt={kit:{kit:"fak"},"kit-duotone":{"kit-duotone":"fakd"}},nt={GROUP:"duotone-group",SWAP_OPACITY:"swap-opacity",PRIMARY:"primary",SECONDARY:"secondary"},En=["fa-classic","fa-duotone","fa-sharp","fa-sharp-duotone"],In=["fak","fa-kit","fakd","fa-kit-duotone"],Cn={"Font Awesome Kit":{400:"fak",normal:"fak"},"Font Awesome Kit Duotone":{400:"fakd",normal:"fakd"}},Nn={classic:{"fa-brands":"fab","fa-duotone":"fad","fa-light":"fal","fa-regular":"far","fa-solid":"fas","fa-thin":"fat"},duotone:{"fa-regular":"fadr","fa-light":"fadl","fa-thin":"fadt"},sharp:{"fa-solid":"fass","fa-regular":"fasr","fa-light":"fasl","fa-thin":"fast"},"sharp-duotone":{"fa-solid":"fasds","fa-regular":"fasdr","fa-light":"fasdl","fa-thin":"fasdt"}},_n={classic:["fas","far","fal","fat","fad"],duotone:["fadr","fadl","fadt"],sharp:["fass","fasr","fasl","fast"],"sharp-duotone":["fasds","fasdr","fasdl","fasdt"]},vt={classic:{fab:"fa-brands",fad:"fa-duotone",fal:"fa-light",far:"fa-regular",fas:"fa-solid",fat:"fa-thin"},duotone:{fadr:"fa-regular",fadl:"fa-light",fadt:"fa-thin"},sharp:{fass:"fa-solid",fasr:"fa-regular",fasl:"fa-light",fast:"fa-thin"},"sharp-duotone":{fasds:"fa-solid",fasdr:"fa-regular",fasdl:"fa-light",fasdt:"fa-thin"}},Tn=["fa-solid","fa-regular","fa-light","fa-thin","fa-duotone","fa-brands"],xt=["fa","fas","far","fal","fat","fad","fadr","fadl","fadt","fab","fass","fasr","fasl","fast","fasds","fasdr","fasdl","fasdt",...En,...Tn],Fn=["solid","regular","light","thin","duotone","brands"],Ne=[1,2,3,4,5,6,7,8,9,10],Mn=Ne.concat([11,12,13,14,15,16,17,18,19,20]),Ln=[...Object.keys(_n),...Fn,"2xs","xs","sm","lg","xl","2xl","beat","border","fade","beat-fade","bounce","flip-both","flip-horizontal","flip-vertical","flip","fw","inverse","layers-counter","layers-text","layers","li","pull-left","pull-right","pulse","rotate-180","rotate-270","rotate-90","rotate-by","shake","spin-pulse","spin-reverse","spin","stack-1x","stack-2x","stack","ul",nt.GROUP,nt.SWAP_OPACITY,nt.PRIMARY,nt.SECONDARY].concat(Ne.map(t=>"".concat(t,"x"))).concat(Mn.map(t=>"w-".concat(t))),zn={"Font Awesome 5 Free":{900:"fas",400:"far"},"Font Awesome 5 Pro":{900:"fas",400:"far",normal:"far",300:"fal"},"Font Awesome 5 Brands":{400:"fab",normal:"fab"},"Font Awesome 5 Duotone":{900:"fad"}};const _="___FONT_AWESOME___",At=16,_e="fa",Te="svg-inline--fa",Y="data-fa-i2svg",wt="data-fa-pseudo-element",Dn="data-fa-pseudo-element-pending",Dt="data-prefix",jt="data-icon",te="fontawesome-i2svg",jn="async",Rn=["HTML","HEAD","STYLE","SCRIPT"],Fe=(()=>{try{return!0}catch{return!1}})();function Z(t){return new Proxy(t,{get(e,n){return n in e?e[n]:e[A]}})}const Me=l({},Ee);Me[A]=l(l(l(l({},{"fa-duotone":"duotone"}),Ee[A]),Zt.kit),Zt["kit-duotone"]);const Yn=Z(Me),Ot=l({},An);Ot[A]=l(l(l(l({},{duotone:"fad"}),Ot[A]),Jt.kit),Jt["kit-duotone"]);const ee=Z(Ot),St=l({},vt);St[A]=l(l({},St[A]),kn.kit);const Rt=Z(St),Pt=l({},Nn);Pt[A]=l(l({},Pt[A]),Sn.kit);Z(Pt);const Un=mn,Le="fa-layers-text",Wn=gn,Bn=l({},bn);Z(Bn);const Gn=["class","data-prefix","data-icon","data-fa-transform","data-fa-mask"],mt=pn,Hn=[...On,...Ln],K=L.FontAwesomeConfig||{};function $n(t){var e=y.querySelector("script["+t+"]");if(e)return e.getAttribute(t)}function Xn(t){return t===""?!0:t==="false"?!1:t==="true"?!0:t}y&&typeof y.querySelector=="function"&&[["data-family-prefix","familyPrefix"],["data-css-prefix","cssPrefix"],["data-family-default","familyDefault"],["data-style-default","styleDefault"],["data-replacement-class","replacementClass"],["data-auto-replace-svg","autoReplaceSvg"],["data-auto-add-css","autoAddCss"],["data-auto-a11y","autoA11y"],["data-search-pseudo-elements","searchPseudoElements"],["data-observe-mutations","observeMutations"],["data-mutate-approach","mutateApproach"],["data-keep-original-source","keepOriginalSource"],["data-measure-performance","measurePerformance"],["data-show-missing-icons","showMissingIcons"]].forEach(e=>{let[n,a]=e;const r=Xn($n(n));r!=null&&(K[a]=r)});const ze={styleDefault:"solid",familyDefault:A,cssPrefix:_e,replacementClass:Te,autoReplaceSvg:!0,autoAddCss:!0,autoA11y:!0,searchPseudoElements:!1,observeMutations:!0,mutateApproach:"async",keepOriginalSource:!0,measurePerformance:!1,showMissingIcons:!0};K.familyPrefix&&(K.cssPrefix=K.familyPrefix);const H=l(l({},ze),K);H.autoReplaceSvg||(H.observeMutations=!1);const c={};Object.keys(ze).forEach(t=>{Object.defineProperty(c,t,{enumerable:!0,set:function(e){H[t]=e,V.forEach(n=>n(c))},get:function(){return H[t]}})});Object.defineProperty(c,"familyPrefix",{enumerable:!0,set:function(t){H.cssPrefix=t,V.forEach(e=>e(c))},get:function(){return H.cssPrefix}});L.FontAwesomeConfig=c;const V=[];function Kn(t){return V.push(t),()=>{V.splice(V.indexOf(t),1)}}const M=At,I={size:16,x:0,y:0,rotate:0,flipX:!1,flipY:!1};function Vn(t){if(!t||!F)return;const e=y.createElement("style");e.setAttribute("type","text/css"),e.innerHTML=t;const n=y.head.childNodes;let a=null;for(let r=n.length-1;r>-1;r--){const i=n[r],o=(i.tagName||"").toUpperCase();["STYLE","LINK"].indexOf(o)>-1&&(a=i)}return y.head.insertBefore(e,a),t}const qn="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";function q(){let t=12,e="";for(;t-- >0;)e+=qn[Math.random()*62|0];return e}function $(t){const e=[];for(let n=(t||[]).length>>>0;n--;)e[n]=t[n];return e}function Yt(t){return t.classList?$(t.classList):(t.getAttribute("class")||"").split(" ").filter(e=>e)}function De(t){return"".concat(t).replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/'/g,"&#39;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}function Qn(t){return Object.keys(t||{}).reduce((e,n)=>e+"".concat(n,'="').concat(De(t[n]),'" '),"").trim()}function ft(t){return Object.keys(t||{}).reduce((e,n)=>e+"".concat(n,": ").concat(t[n].trim(),";"),"")}function Ut(t){return t.size!==I.size||t.x!==I.x||t.y!==I.y||t.rotate!==I.rotate||t.flipX||t.flipY}function Zn(t){let{transform:e,containerWidth:n,iconWidth:a}=t;const r={transform:"translate(".concat(n/2," 256)")},i="translate(".concat(e.x*32,", ").concat(e.y*32,") "),o="scale(".concat(e.size/16*(e.flipX?-1:1),", ").concat(e.size/16*(e.flipY?-1:1),") "),s="rotate(".concat(e.rotate," 0 0)"),u={transform:"".concat(i," ").concat(o," ").concat(s)},f={transform:"translate(".concat(a/2*-1," -256)")};return{outer:r,inner:u,path:f}}function Jn(t){let{transform:e,width:n=At,height:a=At,startCentered:r=!1}=t,i="";return r&&ke?i+="translate(".concat(e.x/M-n/2,"em, ").concat(e.y/M-a/2,"em) "):r?i+="translate(calc(-50% + ".concat(e.x/M,"em), calc(-50% + ").concat(e.y/M,"em)) "):i+="translate(".concat(e.x/M,"em, ").concat(e.y/M,"em) "),i+="scale(".concat(e.size/M*(e.flipX?-1:1),", ").concat(e.size/M*(e.flipY?-1:1),") "),i+="rotate(".concat(e.rotate,"deg) "),i}var ta=`:root, :host {
  --fa-font-solid: normal 900 1em/1 "Font Awesome 6 Free";
  --fa-font-regular: normal 400 1em/1 "Font Awesome 6 Free";
  --fa-font-light: normal 300 1em/1 "Font Awesome 6 Pro";
  --fa-font-thin: normal 100 1em/1 "Font Awesome 6 Pro";
  --fa-font-duotone: normal 900 1em/1 "Font Awesome 6 Duotone";
  --fa-font-duotone-regular: normal 400 1em/1 "Font Awesome 6 Duotone";
  --fa-font-duotone-light: normal 300 1em/1 "Font Awesome 6 Duotone";
  --fa-font-duotone-thin: normal 100 1em/1 "Font Awesome 6 Duotone";
  --fa-font-brands: normal 400 1em/1 "Font Awesome 6 Brands";
  --fa-font-sharp-solid: normal 900 1em/1 "Font Awesome 6 Sharp";
  --fa-font-sharp-regular: normal 400 1em/1 "Font Awesome 6 Sharp";
  --fa-font-sharp-light: normal 300 1em/1 "Font Awesome 6 Sharp";
  --fa-font-sharp-thin: normal 100 1em/1 "Font Awesome 6 Sharp";
  --fa-font-sharp-duotone-solid: normal 900 1em/1 "Font Awesome 6 Sharp Duotone";
  --fa-font-sharp-duotone-regular: normal 400 1em/1 "Font Awesome 6 Sharp Duotone";
  --fa-font-sharp-duotone-light: normal 300 1em/1 "Font Awesome 6 Sharp Duotone";
  --fa-font-sharp-duotone-thin: normal 100 1em/1 "Font Awesome 6 Sharp Duotone";
}

svg:not(:root).svg-inline--fa, svg:not(:host).svg-inline--fa {
  overflow: visible;
  box-sizing: content-box;
}

.svg-inline--fa {
  display: var(--fa-display, inline-block);
  height: 1em;
  overflow: visible;
  vertical-align: -0.125em;
}
.svg-inline--fa.fa-2xs {
  vertical-align: 0.1em;
}
.svg-inline--fa.fa-xs {
  vertical-align: 0em;
}
.svg-inline--fa.fa-sm {
  vertical-align: -0.0714285705em;
}
.svg-inline--fa.fa-lg {
  vertical-align: -0.2em;
}
.svg-inline--fa.fa-xl {
  vertical-align: -0.25em;
}
.svg-inline--fa.fa-2xl {
  vertical-align: -0.3125em;
}
.svg-inline--fa.fa-pull-left {
  margin-right: var(--fa-pull-margin, 0.3em);
  width: auto;
}
.svg-inline--fa.fa-pull-right {
  margin-left: var(--fa-pull-margin, 0.3em);
  width: auto;
}
.svg-inline--fa.fa-li {
  width: var(--fa-li-width, 2em);
  top: 0.25em;
}
.svg-inline--fa.fa-fw {
  width: var(--fa-fw-width, 1.25em);
}

.fa-layers svg.svg-inline--fa {
  bottom: 0;
  left: 0;
  margin: auto;
  position: absolute;
  right: 0;
  top: 0;
}

.fa-layers-counter, .fa-layers-text {
  display: inline-block;
  position: absolute;
  text-align: center;
}

.fa-layers {
  display: inline-block;
  height: 1em;
  position: relative;
  text-align: center;
  vertical-align: -0.125em;
  width: 1em;
}
.fa-layers svg.svg-inline--fa {
  transform-origin: center center;
}

.fa-layers-text {
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  transform-origin: center center;
}

.fa-layers-counter {
  background-color: var(--fa-counter-background-color, #ff253a);
  border-radius: var(--fa-counter-border-radius, 1em);
  box-sizing: border-box;
  color: var(--fa-inverse, #fff);
  line-height: var(--fa-counter-line-height, 1);
  max-width: var(--fa-counter-max-width, 5em);
  min-width: var(--fa-counter-min-width, 1.5em);
  overflow: hidden;
  padding: var(--fa-counter-padding, 0.25em 0.5em);
  right: var(--fa-right, 0);
  text-overflow: ellipsis;
  top: var(--fa-top, 0);
  transform: scale(var(--fa-counter-scale, 0.25));
  transform-origin: top right;
}

.fa-layers-bottom-right {
  bottom: var(--fa-bottom, 0);
  right: var(--fa-right, 0);
  top: auto;
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: bottom right;
}

.fa-layers-bottom-left {
  bottom: var(--fa-bottom, 0);
  left: var(--fa-left, 0);
  right: auto;
  top: auto;
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: bottom left;
}

.fa-layers-top-right {
  top: var(--fa-top, 0);
  right: var(--fa-right, 0);
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: top right;
}

.fa-layers-top-left {
  left: var(--fa-left, 0);
  right: auto;
  top: var(--fa-top, 0);
  transform: scale(var(--fa-layers-scale, 0.25));
  transform-origin: top left;
}

.fa-1x {
  font-size: 1em;
}

.fa-2x {
  font-size: 2em;
}

.fa-3x {
  font-size: 3em;
}

.fa-4x {
  font-size: 4em;
}

.fa-5x {
  font-size: 5em;
}

.fa-6x {
  font-size: 6em;
}

.fa-7x {
  font-size: 7em;
}

.fa-8x {
  font-size: 8em;
}

.fa-9x {
  font-size: 9em;
}

.fa-10x {
  font-size: 10em;
}

.fa-2xs {
  font-size: 0.625em;
  line-height: 0.1em;
  vertical-align: 0.225em;
}

.fa-xs {
  font-size: 0.75em;
  line-height: 0.0833333337em;
  vertical-align: 0.125em;
}

.fa-sm {
  font-size: 0.875em;
  line-height: 0.0714285718em;
  vertical-align: 0.0535714295em;
}

.fa-lg {
  font-size: 1.25em;
  line-height: 0.05em;
  vertical-align: -0.075em;
}

.fa-xl {
  font-size: 1.5em;
  line-height: 0.0416666682em;
  vertical-align: -0.125em;
}

.fa-2xl {
  font-size: 2em;
  line-height: 0.03125em;
  vertical-align: -0.1875em;
}

.fa-fw {
  text-align: center;
  width: 1.25em;
}

.fa-ul {
  list-style-type: none;
  margin-left: var(--fa-li-margin, 2.5em);
  padding-left: 0;
}
.fa-ul > li {
  position: relative;
}

.fa-li {
  left: calc(-1 * var(--fa-li-width, 2em));
  position: absolute;
  text-align: center;
  width: var(--fa-li-width, 2em);
  line-height: inherit;
}

.fa-border {
  border-color: var(--fa-border-color, #eee);
  border-radius: var(--fa-border-radius, 0.1em);
  border-style: var(--fa-border-style, solid);
  border-width: var(--fa-border-width, 0.08em);
  padding: var(--fa-border-padding, 0.2em 0.25em 0.15em);
}

.fa-pull-left {
  float: left;
  margin-right: var(--fa-pull-margin, 0.3em);
}

.fa-pull-right {
  float: right;
  margin-left: var(--fa-pull-margin, 0.3em);
}

.fa-beat {
  animation-name: fa-beat;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-bounce {
  animation-name: fa-bounce;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, cubic-bezier(0.28, 0.84, 0.42, 1));
}

.fa-fade {
  animation-name: fa-fade;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, cubic-bezier(0.4, 0, 0.6, 1));
}

.fa-beat-fade {
  animation-name: fa-beat-fade;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, cubic-bezier(0.4, 0, 0.6, 1));
}

.fa-flip {
  animation-name: fa-flip;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, ease-in-out);
}

.fa-shake {
  animation-name: fa-shake;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, linear);
}

.fa-spin {
  animation-name: fa-spin;
  animation-delay: var(--fa-animation-delay, 0s);
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 2s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, linear);
}

.fa-spin-reverse {
  --fa-animation-direction: reverse;
}

.fa-pulse,
.fa-spin-pulse {
  animation-name: fa-spin;
  animation-direction: var(--fa-animation-direction, normal);
  animation-duration: var(--fa-animation-duration, 1s);
  animation-iteration-count: var(--fa-animation-iteration-count, infinite);
  animation-timing-function: var(--fa-animation-timing, steps(8));
}

@media (prefers-reduced-motion: reduce) {
  .fa-beat,
.fa-bounce,
.fa-fade,
.fa-beat-fade,
.fa-flip,
.fa-pulse,
.fa-shake,
.fa-spin,
.fa-spin-pulse {
    animation-delay: -1ms;
    animation-duration: 1ms;
    animation-iteration-count: 1;
    transition-delay: 0s;
    transition-duration: 0s;
  }
}
@keyframes fa-beat {
  0%, 90% {
    transform: scale(1);
  }
  45% {
    transform: scale(var(--fa-beat-scale, 1.25));
  }
}
@keyframes fa-bounce {
  0% {
    transform: scale(1, 1) translateY(0);
  }
  10% {
    transform: scale(var(--fa-bounce-start-scale-x, 1.1), var(--fa-bounce-start-scale-y, 0.9)) translateY(0);
  }
  30% {
    transform: scale(var(--fa-bounce-jump-scale-x, 0.9), var(--fa-bounce-jump-scale-y, 1.1)) translateY(var(--fa-bounce-height, -0.5em));
  }
  50% {
    transform: scale(var(--fa-bounce-land-scale-x, 1.05), var(--fa-bounce-land-scale-y, 0.95)) translateY(0);
  }
  57% {
    transform: scale(1, 1) translateY(var(--fa-bounce-rebound, -0.125em));
  }
  64% {
    transform: scale(1, 1) translateY(0);
  }
  100% {
    transform: scale(1, 1) translateY(0);
  }
}
@keyframes fa-fade {
  50% {
    opacity: var(--fa-fade-opacity, 0.4);
  }
}
@keyframes fa-beat-fade {
  0%, 100% {
    opacity: var(--fa-beat-fade-opacity, 0.4);
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(var(--fa-beat-fade-scale, 1.125));
  }
}
@keyframes fa-flip {
  50% {
    transform: rotate3d(var(--fa-flip-x, 0), var(--fa-flip-y, 1), var(--fa-flip-z, 0), var(--fa-flip-angle, -180deg));
  }
}
@keyframes fa-shake {
  0% {
    transform: rotate(-15deg);
  }
  4% {
    transform: rotate(15deg);
  }
  8%, 24% {
    transform: rotate(-18deg);
  }
  12%, 28% {
    transform: rotate(18deg);
  }
  16% {
    transform: rotate(-22deg);
  }
  20% {
    transform: rotate(22deg);
  }
  32% {
    transform: rotate(-12deg);
  }
  36% {
    transform: rotate(12deg);
  }
  40%, 100% {
    transform: rotate(0deg);
  }
}
@keyframes fa-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.fa-rotate-90 {
  transform: rotate(90deg);
}

.fa-rotate-180 {
  transform: rotate(180deg);
}

.fa-rotate-270 {
  transform: rotate(270deg);
}

.fa-flip-horizontal {
  transform: scale(-1, 1);
}

.fa-flip-vertical {
  transform: scale(1, -1);
}

.fa-flip-both,
.fa-flip-horizontal.fa-flip-vertical {
  transform: scale(-1, -1);
}

.fa-rotate-by {
  transform: rotate(var(--fa-rotate-angle, 0));
}

.fa-stack {
  display: inline-block;
  vertical-align: middle;
  height: 2em;
  position: relative;
  width: 2.5em;
}

.fa-stack-1x,
.fa-stack-2x {
  bottom: 0;
  left: 0;
  margin: auto;
  position: absolute;
  right: 0;
  top: 0;
  z-index: var(--fa-stack-z-index, auto);
}

.svg-inline--fa.fa-stack-1x {
  height: 1em;
  width: 1.25em;
}
.svg-inline--fa.fa-stack-2x {
  height: 2em;
  width: 2.5em;
}

.fa-inverse {
  color: var(--fa-inverse, #fff);
}

.sr-only,
.fa-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.sr-only-focusable:not(:focus),
.fa-sr-only-focusable:not(:focus) {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.svg-inline--fa .fa-primary {
  fill: var(--fa-primary-color, currentColor);
  opacity: var(--fa-primary-opacity, 1);
}

.svg-inline--fa .fa-secondary {
  fill: var(--fa-secondary-color, currentColor);
  opacity: var(--fa-secondary-opacity, 0.4);
}

.svg-inline--fa.fa-swap-opacity .fa-primary {
  opacity: var(--fa-secondary-opacity, 0.4);
}

.svg-inline--fa.fa-swap-opacity .fa-secondary {
  opacity: var(--fa-primary-opacity, 1);
}

.svg-inline--fa mask .fa-primary,
.svg-inline--fa mask .fa-secondary {
  fill: black;
}`;function je(){const t=_e,e=Te,n=c.cssPrefix,a=c.replacementClass;let r=ta;if(n!==t||a!==e){const i=new RegExp("\\.".concat(t,"\\-"),"g"),o=new RegExp("\\--".concat(t,"\\-"),"g"),s=new RegExp("\\.".concat(e),"g");r=r.replace(i,".".concat(n,"-")).replace(o,"--".concat(n,"-")).replace(s,".".concat(a))}return r}let ne=!1;function gt(){c.autoAddCss&&!ne&&(Vn(je()),ne=!0)}var ea={mixout(){return{dom:{css:je,insertCss:gt}}},hooks(){return{beforeDOMElementCreation(){gt()},beforeI2svg(){gt()}}}};const T=L||{};T[_]||(T[_]={});T[_].styles||(T[_].styles={});T[_].hooks||(T[_].hooks={});T[_].shims||(T[_].shims=[]);var C=T[_];const Re=[],Ye=function(){y.removeEventListener("DOMContentLoaded",Ye),it=1,Re.map(t=>t())};let it=!1;F&&(it=(y.documentElement.doScroll?/^loaded|^c/:/^loaded|^i|^c/).test(y.readyState),it||y.addEventListener("DOMContentLoaded",Ye));function na(t){F&&(it?setTimeout(t,0):Re.push(t))}function J(t){const{tag:e,attributes:n={},children:a=[]}=t;return typeof t=="string"?De(t):"<".concat(e," ").concat(Qn(n),">").concat(a.map(J).join(""),"</").concat(e,">")}function ae(t,e,n){if(t&&t[e]&&t[e][n])return{prefix:e,iconName:n,icon:t[e][n]}}var pt=function(e,n,a,r){var i=Object.keys(e),o=i.length,s=n,u,f,m;for(a===void 0?(u=1,m=e[i[0]]):(u=0,m=a);u<o;u++)f=i[u],m=s(m,e[f],f,e);return m};function aa(t){const e=[];let n=0;const a=t.length;for(;n<a;){const r=t.charCodeAt(n++);if(r>=55296&&r<=56319&&n<a){const i=t.charCodeAt(n++);(i&64512)==56320?e.push(((r&1023)<<10)+(i&1023)+65536):(e.push(r),n--)}else e.push(r)}return e}function kt(t){const e=aa(t);return e.length===1?e[0].toString(16):null}function ra(t,e){const n=t.length;let a=t.charCodeAt(e),r;return a>=55296&&a<=56319&&n>e+1&&(r=t.charCodeAt(e+1),r>=56320&&r<=57343)?(a-55296)*1024+r-56320+65536:a}function re(t){return Object.keys(t).reduce((e,n)=>{const a=t[n];return!!a.icon?e[a.iconName]=a.icon:e[n]=a,e},{})}function Et(t,e){let n=arguments.length>2&&arguments[2]!==void 0?arguments[2]:{};const{skipHooks:a=!1}=n,r=re(e);typeof C.hooks.addPack=="function"&&!a?C.hooks.addPack(t,re(e)):C.styles[t]=l(l({},C.styles[t]||{}),r),t==="fas"&&Et("fa",e)}const{styles:Q,shims:ia}=C,Ue=Object.keys(Rt),oa=Ue.reduce((t,e)=>(t[e]=Object.keys(Rt[e]),t),{});let Wt=null,We={},Be={},Ge={},He={},$e={};function sa(t){return~Hn.indexOf(t)}function la(t,e){const n=e.split("-"),a=n[0],r=n.slice(1).join("-");return a===t&&r!==""&&!sa(r)?r:null}const Xe=()=>{const t=a=>pt(Q,(r,i,o)=>(r[o]=pt(i,a,{}),r),{});We=t((a,r,i)=>(r[3]&&(a[r[3]]=i),r[2]&&r[2].filter(s=>typeof s=="number").forEach(s=>{a[s.toString(16)]=i}),a)),Be=t((a,r,i)=>(a[i]=i,r[2]&&r[2].filter(s=>typeof s=="string").forEach(s=>{a[s]=i}),a)),$e=t((a,r,i)=>{const o=r[2];return a[i]=i,o.forEach(s=>{a[s]=i}),a});const e="far"in Q||c.autoFetchSvg,n=pt(ia,(a,r)=>{const i=r[0];let o=r[1];const s=r[2];return o==="far"&&!e&&(o="fas"),typeof i=="string"&&(a.names[i]={prefix:o,iconName:s}),typeof i=="number"&&(a.unicodes[i.toString(16)]={prefix:o,iconName:s}),a},{names:{},unicodes:{}});Ge=n.names,He=n.unicodes,Wt=ct(c.styleDefault,{family:c.familyDefault})};Kn(t=>{Wt=ct(t.styleDefault,{family:c.familyDefault})});Xe();function Bt(t,e){return(We[t]||{})[e]}function fa(t,e){return(Be[t]||{})[e]}function R(t,e){return($e[t]||{})[e]}function Ke(t){return Ge[t]||{prefix:null,iconName:null}}function ca(t){const e=He[t],n=Bt("fas",t);return e||(n?{prefix:"fas",iconName:n}:null)||{prefix:null,iconName:null}}function z(){return Wt}const Ve=()=>({prefix:null,iconName:null,rest:[]});function ua(t){let e=A;const n=Ue.reduce((a,r)=>(a[r]="".concat(c.cssPrefix,"-").concat(r),a),{});return Ce.forEach(a=>{(t.includes(n[a])||t.some(r=>oa[a].includes(r)))&&(e=a)}),e}function ct(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const{family:n=A}=e,a=Yn[n][t];if(n===lt&&!t)return"fad";const r=ee[n][t]||ee[n][a],i=t in C.styles?t:null;return r||i||null}function da(t){let e=[],n=null;return t.forEach(a=>{const r=la(c.cssPrefix,a);r?n=r:a&&e.push(a)}),{iconName:n,rest:e}}function ie(t){return t.sort().filter((e,n,a)=>a.indexOf(e)===n)}function ut(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const{skipLookups:n=!1}=e;let a=null;const r=xt.concat(In),i=ie(t.filter(h=>r.includes(h))),o=ie(t.filter(h=>!xt.includes(h))),s=i.filter(h=>(a=h,!Ie.includes(h))),[u=null]=s,f=ua(i),m=l(l({},da(o)),{},{prefix:ct(u,{family:f})});return l(l(l({},m),ha({values:t,family:f,styles:Q,config:c,canonical:m,givenPrefix:a})),ma(n,a,m))}function ma(t,e,n){let{prefix:a,iconName:r}=n;if(t||!a||!r)return{prefix:a,iconName:r};const i=e==="fa"?Ke(r):{},o=R(a,r);return r=i.iconName||o||r,a=i.prefix||a,a==="far"&&!Q.far&&Q.fas&&!c.autoFetchSvg&&(a="fas"),{prefix:a,iconName:r}}const ga=Ce.filter(t=>t!==A||t!==lt),pa=Object.keys(vt).filter(t=>t!==A).map(t=>Object.keys(vt[t])).flat();function ha(t){const{values:e,family:n,canonical:a,givenPrefix:r="",styles:i={},config:o={}}=t,s=n===lt,u=e.includes("fa-duotone")||e.includes("fad"),f=o.familyDefault==="duotone",m=a.prefix==="fad"||a.prefix==="fa-duotone";if(!s&&(u||f||m)&&(a.prefix="fad"),(e.includes("fa-brands")||e.includes("fab"))&&(a.prefix="fab"),!a.prefix&&ga.includes(n)&&(Object.keys(i).find(p=>pa.includes(p))||o.autoFetchSvg)){const p=xn.get(n).defaultShortPrefixId;a.prefix=p,a.iconName=R(a.prefix,a.iconName)||a.iconName}return(a.prefix==="fa"||r==="fa")&&(a.prefix=z()||"fas"),a}class ya{constructor(){this.definitions={}}add(){for(var e=arguments.length,n=new Array(e),a=0;a<e;a++)n[a]=arguments[a];const r=n.reduce(this._pullDefinitions,{});Object.keys(r).forEach(i=>{this.definitions[i]=l(l({},this.definitions[i]||{}),r[i]),Et(i,r[i]);const o=Rt[A][i];o&&Et(o,r[i]),Xe()})}reset(){this.definitions={}}_pullDefinitions(e,n){const a=n.prefix&&n.iconName&&n.icon?{0:n}:n;return Object.keys(a).map(r=>{const{prefix:i,iconName:o,icon:s}=a[r],u=s[2];e[i]||(e[i]={}),u.length>0&&u.forEach(f=>{typeof f=="string"&&(e[i][f]=s)}),e[i][o]=s}),e}}let oe=[],B={};const G={},ba=Object.keys(G);function va(t,e){let{mixoutsTo:n}=e;return oe=t,B={},Object.keys(G).forEach(a=>{ba.indexOf(a)===-1&&delete G[a]}),oe.forEach(a=>{const r=a.mixout?a.mixout():{};if(Object.keys(r).forEach(i=>{typeof r[i]=="function"&&(n[i]=r[i]),typeof r[i]=="object"&&Object.keys(r[i]).forEach(o=>{n[i]||(n[i]={}),n[i][o]=r[i][o]})}),a.hooks){const i=a.hooks();Object.keys(i).forEach(o=>{B[o]||(B[o]=[]),B[o].push(i[o])})}a.provides&&a.provides(G)}),n}function It(t,e){for(var n=arguments.length,a=new Array(n>2?n-2:0),r=2;r<n;r++)a[r-2]=arguments[r];return(B[t]||[]).forEach(o=>{e=o.apply(null,[e,...a])}),e}function U(t){for(var e=arguments.length,n=new Array(e>1?e-1:0),a=1;a<e;a++)n[a-1]=arguments[a];(B[t]||[]).forEach(i=>{i.apply(null,n)})}function D(){const t=arguments[0],e=Array.prototype.slice.call(arguments,1);return G[t]?G[t].apply(null,e):void 0}function Ct(t){t.prefix==="fa"&&(t.prefix="fas");let{iconName:e}=t;const n=t.prefix||z();if(e)return e=R(n,e)||e,ae(qe.definitions,n,e)||ae(C.styles,n,e)}const qe=new ya,xa=()=>{c.autoReplaceSvg=!1,c.observeMutations=!1,U("noAuto")},Aa={i2svg:function(){let t=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{};return F?(U("beforeI2svg",t),D("pseudoElements2svg",t),D("i2svg",t)):Promise.reject(new Error("Operation requires a DOM of some kind."))},watch:function(){let t=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{};const{autoReplaceSvgRoot:e}=t;c.autoReplaceSvg===!1&&(c.autoReplaceSvg=!0),c.observeMutations=!0,na(()=>{Oa({autoReplaceSvgRoot:e}),U("watch",t)})}},wa={icon:t=>{if(t===null)return null;if(typeof t=="object"&&t.prefix&&t.iconName)return{prefix:t.prefix,iconName:R(t.prefix,t.iconName)||t.iconName};if(Array.isArray(t)&&t.length===2){const e=t[1].indexOf("fa-")===0?t[1].slice(3):t[1],n=ct(t[0]);return{prefix:n,iconName:R(n,e)||e}}if(typeof t=="string"&&(t.indexOf("".concat(c.cssPrefix,"-"))>-1||t.match(Un))){const e=ut(t.split(" "),{skipLookups:!0});return{prefix:e.prefix||z(),iconName:R(e.prefix,e.iconName)||e.iconName}}if(typeof t=="string"){const e=z();return{prefix:e,iconName:R(e,t)||t}}}},S={noAuto:xa,config:c,dom:Aa,parse:wa,library:qe,findIconDefinition:Ct,toHtml:J},Oa=function(){let t=arguments.length>0&&arguments[0]!==void 0?arguments[0]:{};const{autoReplaceSvgRoot:e=y}=t;(Object.keys(C.styles).length>0||c.autoFetchSvg)&&F&&c.autoReplaceSvg&&S.dom.i2svg({node:e})};function dt(t,e){return Object.defineProperty(t,"abstract",{get:e}),Object.defineProperty(t,"html",{get:function(){return t.abstract.map(n=>J(n))}}),Object.defineProperty(t,"node",{get:function(){if(!F)return;const n=y.createElement("div");return n.innerHTML=t.html,n.children}}),t}function Sa(t){let{children:e,main:n,mask:a,attributes:r,styles:i,transform:o}=t;if(Ut(o)&&n.found&&!a.found){const{width:s,height:u}=n,f={x:s/u/2,y:.5};r.style=ft(l(l({},i),{},{"transform-origin":"".concat(f.x+o.x/16,"em ").concat(f.y+o.y/16,"em")}))}return[{tag:"svg",attributes:r,children:e}]}function Pa(t){let{prefix:e,iconName:n,children:a,attributes:r,symbol:i}=t;const o=i===!0?"".concat(e,"-").concat(c.cssPrefix,"-").concat(n):i;return[{tag:"svg",attributes:{style:"display: none;"},children:[{tag:"symbol",attributes:l(l({},r),{},{id:o}),children:a}]}]}function Gt(t){const{icons:{main:e,mask:n},prefix:a,iconName:r,transform:i,symbol:o,title:s,maskId:u,titleId:f,extra:m,watchable:h=!1}=t,{width:p,height:v}=n.found?n:e,E=Pn.includes(a),k=[c.replacementClass,r?"".concat(c.cssPrefix,"-").concat(r):""].filter(P=>m.classes.indexOf(P)===-1).filter(P=>P!==""||!!P).concat(m.classes).join(" ");let w={children:[],attributes:l(l({},m.attributes),{},{"data-prefix":a,"data-icon":r,class:k,role:m.attributes.role||"img",xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 ".concat(p," ").concat(v)})};const d=E&&!~m.classes.indexOf("fa-fw")?{width:"".concat(p/v*16*.0625,"em")}:{};h&&(w.attributes[Y]=""),s&&(w.children.push({tag:"title",attributes:{id:w.attributes["aria-labelledby"]||"title-".concat(f||q())},children:[s]}),delete w.attributes.title);const g=l(l({},w),{},{prefix:a,iconName:r,main:e,mask:n,maskId:u,transform:i,symbol:o,styles:l(l({},d),m.styles)}),{children:b,attributes:x}=n.found&&e.found?D("generateAbstractMask",g)||{children:[],attributes:{}}:D("generateAbstractIcon",g)||{children:[],attributes:{}};return g.children=b,g.attributes=x,o?Pa(g):Sa(g)}function se(t){const{content:e,width:n,height:a,transform:r,title:i,extra:o,watchable:s=!1}=t,u=l(l(l({},o.attributes),i?{title:i}:{}),{},{class:o.classes.join(" ")});s&&(u[Y]="");const f=l({},o.styles);Ut(r)&&(f.transform=Jn({transform:r,startCentered:!0,width:n,height:a}),f["-webkit-transform"]=f.transform);const m=ft(f);m.length>0&&(u.style=m);const h=[];return h.push({tag:"span",attributes:u,children:[e]}),i&&h.push({tag:"span",attributes:{class:"sr-only"},children:[i]}),h}function ka(t){const{content:e,title:n,extra:a}=t,r=l(l(l({},a.attributes),n?{title:n}:{}),{},{class:a.classes.join(" ")}),i=ft(a.styles);i.length>0&&(r.style=i);const o=[];return o.push({tag:"span",attributes:r,children:[e]}),n&&o.push({tag:"span",attributes:{class:"sr-only"},children:[n]}),o}const{styles:ht}=C;function Nt(t){const e=t[0],n=t[1],[a]=t.slice(4);let r=null;return Array.isArray(a)?r={tag:"g",attributes:{class:"".concat(c.cssPrefix,"-").concat(mt.GROUP)},children:[{tag:"path",attributes:{class:"".concat(c.cssPrefix,"-").concat(mt.SECONDARY),fill:"currentColor",d:a[0]}},{tag:"path",attributes:{class:"".concat(c.cssPrefix,"-").concat(mt.PRIMARY),fill:"currentColor",d:a[1]}}]}:r={tag:"path",attributes:{fill:"currentColor",d:a}},{found:!0,width:e,height:n,icon:r}}const Ea={found:!1,width:512,height:512};function Ia(t,e){!Fe&&!c.showMissingIcons&&t&&console.error('Icon with name "'.concat(t,'" and prefix "').concat(e,'" is missing.'))}function _t(t,e){let n=e;return e==="fa"&&c.styleDefault!==null&&(e=z()),new Promise((a,r)=>{if(n==="fa"){const i=Ke(t)||{};t=i.iconName||t,e=i.prefix||e}if(t&&e&&ht[e]&&ht[e][t]){const i=ht[e][t];return a(Nt(i))}Ia(t,e),a(l(l({},Ea),{},{icon:c.showMissingIcons&&t?D("missingIconAbstract")||{}:{}}))})}const le=()=>{},Tt=c.measurePerformance&&et&&et.mark&&et.measure?et:{mark:le,measure:le},X='FA "6.7.1"',Ca=t=>(Tt.mark("".concat(X," ").concat(t," begins")),()=>Qe(t)),Qe=t=>{Tt.mark("".concat(X," ").concat(t," ends")),Tt.measure("".concat(X," ").concat(t),"".concat(X," ").concat(t," begins"),"".concat(X," ").concat(t," ends"))};var Ht={begin:Ca,end:Qe};const at=()=>{};function fe(t){return typeof(t.getAttribute?t.getAttribute(Y):null)=="string"}function Na(t){const e=t.getAttribute?t.getAttribute(Dt):null,n=t.getAttribute?t.getAttribute(jt):null;return e&&n}function _a(t){return t&&t.classList&&t.classList.contains&&t.classList.contains(c.replacementClass)}function Ta(){return c.autoReplaceSvg===!0?rt.replace:rt[c.autoReplaceSvg]||rt.replace}function Fa(t){return y.createElementNS("http://www.w3.org/2000/svg",t)}function Ma(t){return y.createElement(t)}function Ze(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const{ceFn:n=t.tag==="svg"?Fa:Ma}=e;if(typeof t=="string")return y.createTextNode(t);const a=n(t.tag);return Object.keys(t.attributes||[]).forEach(function(i){a.setAttribute(i,t.attributes[i])}),(t.children||[]).forEach(function(i){a.appendChild(Ze(i,{ceFn:n}))}),a}function La(t){let e=" ".concat(t.outerHTML," ");return e="".concat(e,"Font Awesome fontawesome.com "),e}const rt={replace:function(t){const e=t[0];if(e.parentNode)if(t[1].forEach(n=>{e.parentNode.insertBefore(Ze(n),e)}),e.getAttribute(Y)===null&&c.keepOriginalSource){let n=y.createComment(La(e));e.parentNode.replaceChild(n,e)}else e.remove()},nest:function(t){const e=t[0],n=t[1];if(~Yt(e).indexOf(c.replacementClass))return rt.replace(t);const a=new RegExp("".concat(c.cssPrefix,"-.*"));if(delete n[0].attributes.id,n[0].attributes.class){const i=n[0].attributes.class.split(" ").reduce((o,s)=>(s===c.replacementClass||s.match(a)?o.toSvg.push(s):o.toNode.push(s),o),{toNode:[],toSvg:[]});n[0].attributes.class=i.toSvg.join(" "),i.toNode.length===0?e.removeAttribute("class"):e.setAttribute("class",i.toNode.join(" "))}const r=n.map(i=>J(i)).join(`
`);e.setAttribute(Y,""),e.innerHTML=r}};function ce(t){t()}function Je(t,e){const n=typeof e=="function"?e:at;if(t.length===0)n();else{let a=ce;c.mutateApproach===jn&&(a=L.requestAnimationFrame||ce),a(()=>{const r=Ta(),i=Ht.begin("mutate");t.map(r),i(),n()})}}let $t=!1;function tn(){$t=!0}function Ft(){$t=!1}let ot=null;function ue(t){if(!Qt||!c.observeMutations)return;const{treeCallback:e=at,nodeCallback:n=at,pseudoElementsCallback:a=at,observeMutationsRoot:r=y}=t;ot=new Qt(i=>{if($t)return;const o=z();$(i).forEach(s=>{if(s.type==="childList"&&s.addedNodes.length>0&&!fe(s.addedNodes[0])&&(c.searchPseudoElements&&a(s.target),e(s.target)),s.type==="attributes"&&s.target.parentNode&&c.searchPseudoElements&&a(s.target.parentNode),s.type==="attributes"&&fe(s.target)&&~Gn.indexOf(s.attributeName))if(s.attributeName==="class"&&Na(s.target)){const{prefix:u,iconName:f}=ut(Yt(s.target));s.target.setAttribute(Dt,u||o),f&&s.target.setAttribute(jt,f)}else _a(s.target)&&n(s.target)})}),F&&ot.observe(r,{childList:!0,attributes:!0,characterData:!0,subtree:!0})}function za(){ot&&ot.disconnect()}function Da(t){const e=t.getAttribute("style");let n=[];return e&&(n=e.split(";").reduce((a,r)=>{const i=r.split(":"),o=i[0],s=i.slice(1);return o&&s.length>0&&(a[o]=s.join(":").trim()),a},{})),n}function ja(t){const e=t.getAttribute("data-prefix"),n=t.getAttribute("data-icon"),a=t.innerText!==void 0?t.innerText.trim():"";let r=ut(Yt(t));return r.prefix||(r.prefix=z()),e&&n&&(r.prefix=e,r.iconName=n),r.iconName&&r.prefix||(r.prefix&&a.length>0&&(r.iconName=fa(r.prefix,t.innerText)||Bt(r.prefix,kt(t.innerText))),!r.iconName&&c.autoFetchSvg&&t.firstChild&&t.firstChild.nodeType===Node.TEXT_NODE&&(r.iconName=t.firstChild.data)),r}function Ra(t){const e=$(t.attributes).reduce((r,i)=>(r.name!=="class"&&r.name!=="style"&&(r[i.name]=i.value),r),{}),n=t.getAttribute("title"),a=t.getAttribute("data-fa-title-id");return c.autoA11y&&(n?e["aria-labelledby"]="".concat(c.replacementClass,"-title-").concat(a||q()):(e["aria-hidden"]="true",e.focusable="false")),e}function Ya(){return{iconName:null,title:null,titleId:null,prefix:null,transform:I,symbol:!1,mask:{iconName:null,prefix:null,rest:[]},maskId:null,extra:{classes:[],styles:{},attributes:{}}}}function de(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{styleParser:!0};const{iconName:n,prefix:a,rest:r}=ja(t),i=Ra(t),o=It("parseNodeAttributes",{},t);let s=e.styleParser?Da(t):[];return l({iconName:n,title:t.getAttribute("title"),titleId:t.getAttribute("data-fa-title-id"),prefix:a,transform:I,mask:{iconName:null,prefix:null,rest:[]},maskId:null,symbol:!1,extra:{classes:r,styles:s,attributes:i}},o)}const{styles:Ua}=C;function en(t){const e=c.autoReplaceSvg==="nest"?de(t,{styleParser:!1}):de(t);return~e.extra.classes.indexOf(Le)?D("generateLayersText",t,e):D("generateSvgReplacementMutation",t,e)}function Wa(){return[...wn,...xt]}function me(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:null;if(!F)return Promise.resolve();const n=y.documentElement.classList,a=m=>n.add("".concat(te,"-").concat(m)),r=m=>n.remove("".concat(te,"-").concat(m)),i=c.autoFetchSvg?Wa():Ie.concat(Object.keys(Ua));i.includes("fa")||i.push("fa");const o=[".".concat(Le,":not([").concat(Y,"])")].concat(i.map(m=>".".concat(m,":not([").concat(Y,"])"))).join(", ");if(o.length===0)return Promise.resolve();let s=[];try{s=$(t.querySelectorAll(o))}catch{}if(s.length>0)a("pending"),r("complete");else return Promise.resolve();const u=Ht.begin("onTree"),f=s.reduce((m,h)=>{try{const p=en(h);p&&m.push(p)}catch(p){Fe||p.name==="MissingIcon"&&console.error(p)}return m},[]);return new Promise((m,h)=>{Promise.all(f).then(p=>{Je(p,()=>{a("active"),a("complete"),r("pending"),typeof e=="function"&&e(),u(),m()})}).catch(p=>{u(),h(p)})})}function Ba(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:null;en(t).then(n=>{n&&Je([n],e)})}function Ga(t){return function(e){let n=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const a=(e||{}).icon?e:Ct(e||{});let{mask:r}=n;return r&&(r=(r||{}).icon?r:Ct(r||{})),t(a,l(l({},n),{},{mask:r}))}}const Ha=function(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const{transform:n=I,symbol:a=!1,mask:r=null,maskId:i=null,title:o=null,titleId:s=null,classes:u=[],attributes:f={},styles:m={}}=e;if(!t)return;const{prefix:h,iconName:p,icon:v}=t;return dt(l({type:"icon"},t),()=>(U("beforeDOMElementCreation",{iconDefinition:t,params:e}),c.autoA11y&&(o?f["aria-labelledby"]="".concat(c.replacementClass,"-title-").concat(s||q()):(f["aria-hidden"]="true",f.focusable="false")),Gt({icons:{main:Nt(v),mask:r?Nt(r.icon):{found:!1,width:null,height:null,icon:{}}},prefix:h,iconName:p,transform:l(l({},I),n),symbol:a,title:o,maskId:i,titleId:s,extra:{attributes:f,styles:m,classes:u}})))};var $a={mixout(){return{icon:Ga(Ha)}},hooks(){return{mutationObserverCallbacks(t){return t.treeCallback=me,t.nodeCallback=Ba,t}}},provides(t){t.i2svg=function(e){const{node:n=y,callback:a=()=>{}}=e;return me(n,a)},t.generateSvgReplacementMutation=function(e,n){const{iconName:a,title:r,titleId:i,prefix:o,transform:s,symbol:u,mask:f,maskId:m,extra:h}=n;return new Promise((p,v)=>{Promise.all([_t(a,o),f.iconName?_t(f.iconName,f.prefix):Promise.resolve({found:!1,width:512,height:512,icon:{}})]).then(E=>{let[k,w]=E;p([e,Gt({icons:{main:k,mask:w},prefix:o,iconName:a,transform:s,symbol:u,maskId:m,title:r,titleId:i,extra:h,watchable:!0})])}).catch(v)})},t.generateAbstractIcon=function(e){let{children:n,attributes:a,main:r,transform:i,styles:o}=e;const s=ft(o);s.length>0&&(a.style=s);let u;return Ut(i)&&(u=D("generateAbstractTransformGrouping",{main:r,transform:i,containerWidth:r.width,iconWidth:r.width})),n.push(u||r.icon),{children:n,attributes:a}}}},Xa={mixout(){return{layer(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const{classes:n=[]}=e;return dt({type:"layer"},()=>{U("beforeDOMElementCreation",{assembler:t,params:e});let a=[];return t(r=>{Array.isArray(r)?r.map(i=>{a=a.concat(i.abstract)}):a=a.concat(r.abstract)}),[{tag:"span",attributes:{class:["".concat(c.cssPrefix,"-layers"),...n].join(" ")},children:a}]})}}}},Ka={mixout(){return{counter(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const{title:n=null,classes:a=[],attributes:r={},styles:i={}}=e;return dt({type:"counter",content:t},()=>(U("beforeDOMElementCreation",{content:t,params:e}),ka({content:t.toString(),title:n,extra:{attributes:r,styles:i,classes:["".concat(c.cssPrefix,"-layers-counter"),...a]}})))}}}},Va={mixout(){return{text(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{};const{transform:n=I,title:a=null,classes:r=[],attributes:i={},styles:o={}}=e;return dt({type:"text",content:t},()=>(U("beforeDOMElementCreation",{content:t,params:e}),se({content:t,transform:l(l({},I),n),title:a,extra:{attributes:i,styles:o,classes:["".concat(c.cssPrefix,"-layers-text"),...r]}})))}}},provides(t){t.generateLayersText=function(e,n){const{title:a,transform:r,extra:i}=n;let o=null,s=null;if(ke){const u=parseInt(getComputedStyle(e).fontSize,10),f=e.getBoundingClientRect();o=f.width/u,s=f.height/u}return c.autoA11y&&!a&&(i.attributes["aria-hidden"]="true"),Promise.resolve([e,se({content:e.innerHTML,width:o,height:s,transform:r,title:a,extra:i,watchable:!0})])}}};const qa=new RegExp('"',"ug"),ge=[1105920,1112319],pe=l(l(l(l({},{FontAwesome:{normal:"fas",400:"fas"}}),vn),zn),Cn),Mt=Object.keys(pe).reduce((t,e)=>(t[e.toLowerCase()]=pe[e],t),{}),Qa=Object.keys(Mt).reduce((t,e)=>{const n=Mt[e];return t[e]=n[900]||[...Object.entries(n)][0][1],t},{});function Za(t){const e=t.replace(qa,""),n=ra(e,0),a=n>=ge[0]&&n<=ge[1],r=e.length===2?e[0]===e[1]:!1;return{value:kt(r?e[0]:e),isSecondary:a||r}}function Ja(t,e){const n=t.replace(/^['"]|['"]$/g,"").toLowerCase(),a=parseInt(e),r=isNaN(a)?"normal":a;return(Mt[n]||{})[r]||Qa[n]}function he(t,e){const n="".concat(Dn).concat(e.replace(":","-"));return new Promise((a,r)=>{if(t.getAttribute(n)!==null)return a();const o=$(t.children).filter(p=>p.getAttribute(wt)===e)[0],s=L.getComputedStyle(t,e),u=s.getPropertyValue("font-family"),f=u.match(Wn),m=s.getPropertyValue("font-weight"),h=s.getPropertyValue("content");if(o&&!f)return t.removeChild(o),a();if(f&&h!=="none"&&h!==""){const p=s.getPropertyValue("content");let v=Ja(u,m);const{value:E,isSecondary:k}=Za(p),w=f[0].startsWith("FontAwesome");let d=Bt(v,E),g=d;if(w){const b=ca(E);b.iconName&&b.prefix&&(d=b.iconName,v=b.prefix)}if(d&&!k&&(!o||o.getAttribute(Dt)!==v||o.getAttribute(jt)!==g)){t.setAttribute(n,g),o&&t.removeChild(o);const b=Ya(),{extra:x}=b;x.attributes[wt]=e,_t(d,v).then(P=>{const tt=Gt(l(l({},b),{},{icons:{main:P,mask:Ve()},prefix:v,iconName:g,extra:x,watchable:!0})),j=y.createElementNS("http://www.w3.org/2000/svg","svg");e==="::before"?t.insertBefore(j,t.firstChild):t.appendChild(j),j.outerHTML=tt.map(on=>J(on)).join(`
`),t.removeAttribute(n),a()}).catch(r)}else a()}else a()})}function tr(t){return Promise.all([he(t,"::before"),he(t,"::after")])}function er(t){return t.parentNode!==document.head&&!~Rn.indexOf(t.tagName.toUpperCase())&&!t.getAttribute(wt)&&(!t.parentNode||t.parentNode.tagName!=="svg")}function ye(t){if(F)return new Promise((e,n)=>{const a=$(t.querySelectorAll("*")).filter(er).map(tr),r=Ht.begin("searchPseudoElements");tn(),Promise.all(a).then(()=>{r(),Ft(),e()}).catch(()=>{r(),Ft(),n()})})}var nr={hooks(){return{mutationObserverCallbacks(t){return t.pseudoElementsCallback=ye,t}}},provides(t){t.pseudoElements2svg=function(e){const{node:n=y}=e;c.searchPseudoElements&&ye(n)}}};let be=!1;var ar={mixout(){return{dom:{unwatch(){tn(),be=!0}}}},hooks(){return{bootstrap(){ue(It("mutationObserverCallbacks",{}))},noAuto(){za()},watch(t){const{observeMutationsRoot:e}=t;be?Ft():ue(It("mutationObserverCallbacks",{observeMutationsRoot:e}))}}}};const ve=t=>{let e={size:16,x:0,y:0,flipX:!1,flipY:!1,rotate:0};return t.toLowerCase().split(" ").reduce((n,a)=>{const r=a.toLowerCase().split("-"),i=r[0];let o=r.slice(1).join("-");if(i&&o==="h")return n.flipX=!0,n;if(i&&o==="v")return n.flipY=!0,n;if(o=parseFloat(o),isNaN(o))return n;switch(i){case"grow":n.size=n.size+o;break;case"shrink":n.size=n.size-o;break;case"left":n.x=n.x-o;break;case"right":n.x=n.x+o;break;case"up":n.y=n.y-o;break;case"down":n.y=n.y+o;break;case"rotate":n.rotate=n.rotate+o;break}return n},e)};var rr={mixout(){return{parse:{transform:t=>ve(t)}}},hooks(){return{parseNodeAttributes(t,e){const n=e.getAttribute("data-fa-transform");return n&&(t.transform=ve(n)),t}}},provides(t){t.generateAbstractTransformGrouping=function(e){let{main:n,transform:a,containerWidth:r,iconWidth:i}=e;const o={transform:"translate(".concat(r/2," 256)")},s="translate(".concat(a.x*32,", ").concat(a.y*32,") "),u="scale(".concat(a.size/16*(a.flipX?-1:1),", ").concat(a.size/16*(a.flipY?-1:1),") "),f="rotate(".concat(a.rotate," 0 0)"),m={transform:"".concat(s," ").concat(u," ").concat(f)},h={transform:"translate(".concat(i/2*-1," -256)")},p={outer:o,inner:m,path:h};return{tag:"g",attributes:l({},p.outer),children:[{tag:"g",attributes:l({},p.inner),children:[{tag:n.icon.tag,children:n.icon.children,attributes:l(l({},n.icon.attributes),p.path)}]}]}}}};const yt={x:0,y:0,width:"100%",height:"100%"};function xe(t){let e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!0;return t.attributes&&(t.attributes.fill||e)&&(t.attributes.fill="black"),t}function ir(t){return t.tag==="g"?t.children:[t]}var or={hooks(){return{parseNodeAttributes(t,e){const n=e.getAttribute("data-fa-mask"),a=n?ut(n.split(" ").map(r=>r.trim())):Ve();return a.prefix||(a.prefix=z()),t.mask=a,t.maskId=e.getAttribute("data-fa-mask-id"),t}}},provides(t){t.generateAbstractMask=function(e){let{children:n,attributes:a,main:r,mask:i,maskId:o,transform:s}=e;const{width:u,icon:f}=r,{width:m,icon:h}=i,p=Zn({transform:s,containerWidth:m,iconWidth:u}),v={tag:"rect",attributes:l(l({},yt),{},{fill:"white"})},E=f.children?{children:f.children.map(xe)}:{},k={tag:"g",attributes:l({},p.inner),children:[xe(l({tag:f.tag,attributes:l(l({},f.attributes),p.path)},E))]},w={tag:"g",attributes:l({},p.outer),children:[k]},d="mask-".concat(o||q()),g="clip-".concat(o||q()),b={tag:"mask",attributes:l(l({},yt),{},{id:d,maskUnits:"userSpaceOnUse",maskContentUnits:"userSpaceOnUse"}),children:[v,w]},x={tag:"defs",children:[{tag:"clipPath",attributes:{id:g},children:ir(h)},b]};return n.push(x,{tag:"rect",attributes:l({fill:"currentColor","clip-path":"url(#".concat(g,")"),mask:"url(#".concat(d,")")},yt)}),{children:n,attributes:a}}}},sr={provides(t){let e=!1;L.matchMedia&&(e=L.matchMedia("(prefers-reduced-motion: reduce)").matches),t.missingIconAbstract=function(){const n=[],a={fill:"currentColor"},r={attributeType:"XML",repeatCount:"indefinite",dur:"2s"};n.push({tag:"path",attributes:l(l({},a),{},{d:"M156.5,447.7l-12.6,29.5c-18.7-9.5-35.9-21.2-51.5-34.9l22.7-22.7C127.6,430.5,141.5,440,156.5,447.7z M40.6,272H8.5 c1.4,21.2,5.4,41.7,11.7,61.1L50,321.2C45.1,305.5,41.8,289,40.6,272z M40.6,240c1.4-18.8,5.2-37,11.1-54.1l-29.5-12.6 C14.7,194.3,10,216.7,8.5,240H40.6z M64.3,156.5c7.8-14.9,17.2-28.8,28.1-41.5L69.7,92.3c-13.7,15.6-25.5,32.8-34.9,51.5 L64.3,156.5z M397,419.6c-13.9,12-29.4,22.3-46.1,30.4l11.9,29.8c20.7-9.9,39.8-22.6,56.9-37.6L397,419.6z M115,92.4 c13.9-12,29.4-22.3,46.1-30.4l-11.9-29.8c-20.7,9.9-39.8,22.6-56.8,37.6L115,92.4z M447.7,355.5c-7.8,14.9-17.2,28.8-28.1,41.5 l22.7,22.7c13.7-15.6,25.5-32.9,34.9-51.5L447.7,355.5z M471.4,272c-1.4,18.8-5.2,37-11.1,54.1l29.5,12.6 c7.5-21.1,12.2-43.5,13.6-66.8H471.4z M321.2,462c-15.7,5-32.2,8.2-49.2,9.4v32.1c21.2-1.4,41.7-5.4,61.1-11.7L321.2,462z M240,471.4c-18.8-1.4-37-5.2-54.1-11.1l-12.6,29.5c21.1,7.5,43.5,12.2,66.8,13.6V471.4z M462,190.8c5,15.7,8.2,32.2,9.4,49.2h32.1 c-1.4-21.2-5.4-41.7-11.7-61.1L462,190.8z M92.4,397c-12-13.9-22.3-29.4-30.4-46.1l-29.8,11.9c9.9,20.7,22.6,39.8,37.6,56.9 L92.4,397z M272,40.6c18.8,1.4,36.9,5.2,54.1,11.1l12.6-29.5C317.7,14.7,295.3,10,272,8.5V40.6z M190.8,50 c15.7-5,32.2-8.2,49.2-9.4V8.5c-21.2,1.4-41.7,5.4-61.1,11.7L190.8,50z M442.3,92.3L419.6,115c12,13.9,22.3,29.4,30.5,46.1 l29.8-11.9C470,128.5,457.3,109.4,442.3,92.3z M397,92.4l22.7-22.7c-15.6-13.7-32.8-25.5-51.5-34.9l-12.6,29.5 C370.4,72.1,384.4,81.5,397,92.4z"})});const i=l(l({},r),{},{attributeName:"opacity"}),o={tag:"circle",attributes:l(l({},a),{},{cx:"256",cy:"364",r:"28"}),children:[]};return e||o.children.push({tag:"animate",attributes:l(l({},r),{},{attributeName:"r",values:"28;14;28;28;14;28;"})},{tag:"animate",attributes:l(l({},i),{},{values:"1;0;1;1;0;1;"})}),n.push(o),n.push({tag:"path",attributes:l(l({},a),{},{opacity:"1",d:"M263.7,312h-16c-6.6,0-12-5.4-12-12c0-71,77.4-63.9,77.4-107.8c0-20-17.8-40.2-57.4-40.2c-29.1,0-44.3,9.6-59.2,28.7 c-3.9,5-11.1,6-16.2,2.4l-13.1-9.2c-5.6-3.9-6.9-11.8-2.6-17.2c21.2-27.2,46.4-44.7,91.2-44.7c52.3,0,97.4,29.8,97.4,80.2 c0,67.6-77.4,63.5-77.4,107.8C275.7,306.6,270.3,312,263.7,312z"}),children:e?[]:[{tag:"animate",attributes:l(l({},i),{},{values:"1;0;0;0;0;1;"})}]}),e||n.push({tag:"path",attributes:l(l({},a),{},{opacity:"0",d:"M232.5,134.5l7,168c0.3,6.4,5.6,11.5,12,11.5h9c6.4,0,11.7-5.1,12-11.5l7-168c0.3-6.8-5.2-12.5-12-12.5h-23 C237.7,122,232.2,127.7,232.5,134.5z"}),children:[{tag:"animate",attributes:l(l({},i),{},{values:"0;0;1;1;0;0;"})}]}),{tag:"g",attributes:{class:"missing"},children:n}}}},lr={hooks(){return{parseNodeAttributes(t,e){const n=e.getAttribute("data-fa-symbol"),a=n===null?!1:n===""?!0:n;return t.symbol=a,t}}}},fr=[ea,$a,Xa,Ka,Va,nr,ar,rr,or,sr,lr];va(fr,{mixoutsTo:S});S.noAuto;S.config;S.library;S.dom;const Lt=S.parse;S.findIconDefinition;S.toHtml;const cr=S.icon;S.layer;S.text;S.counter;function Ae(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);e&&(a=a.filter(function(r){return Object.getOwnPropertyDescriptor(t,r).enumerable})),n.push.apply(n,a)}return n}function N(t){for(var e=1;e<arguments.length;e++){var n=arguments[e]!=null?arguments[e]:{};e%2?Ae(Object(n),!0).forEach(function(a){O(t,a,n[a])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):Ae(Object(n)).forEach(function(a){Object.defineProperty(t,a,Object.getOwnPropertyDescriptor(n,a))})}return t}function ur(t,e){if(typeof t!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var a=n.call(t,e);if(typeof a!="object")return a;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}function dr(t){var e=ur(t,"string");return typeof e=="symbol"?e:e+""}function st(t){"@babel/helpers - typeof";return st=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},st(t)}function O(t,e,n){return e=dr(e),e in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function mr(t,e){if(t==null)return{};var n={};for(var a in t)if(Object.prototype.hasOwnProperty.call(t,a)){if(e.indexOf(a)>=0)continue;n[a]=t[a]}return n}function gr(t,e){if(t==null)return{};var n=mr(t,e),a,r;if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);for(r=0;r<i.length;r++)a=i[r],!(e.indexOf(a)>=0)&&Object.prototype.propertyIsEnumerable.call(t,a)&&(n[a]=t[a])}return n}var pr=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof Xt<"u"?Xt:typeof self<"u"?self:{},nn={exports:{}};(function(t){(function(e){var n=function(d,g,b){if(!f(g)||h(g)||p(g)||v(g)||u(g))return g;var x,P=0,tt=0;if(m(g))for(x=[],tt=g.length;P<tt;P++)x.push(n(d,g[P],b));else{x={};for(var j in g)Object.prototype.hasOwnProperty.call(g,j)&&(x[d(j,b)]=n(d,g[j],b))}return x},a=function(d,g){g=g||{};var b=g.separator||"_",x=g.split||/(?=[A-Z])/;return d.split(x).join(b)},r=function(d){return E(d)?d:(d=d.replace(/[\-_\s]+(.)?/g,function(g,b){return b?b.toUpperCase():""}),d.substr(0,1).toLowerCase()+d.substr(1))},i=function(d){var g=r(d);return g.substr(0,1).toUpperCase()+g.substr(1)},o=function(d,g){return a(d,g).toLowerCase()},s=Object.prototype.toString,u=function(d){return typeof d=="function"},f=function(d){return d===Object(d)},m=function(d){return s.call(d)=="[object Array]"},h=function(d){return s.call(d)=="[object Date]"},p=function(d){return s.call(d)=="[object RegExp]"},v=function(d){return s.call(d)=="[object Boolean]"},E=function(d){return d=d-0,d===d},k=function(d,g){var b=g&&"process"in g?g.process:g;return typeof b!="function"?d:function(x,P){return b(x,d,P)}},w={camelize:r,decamelize:o,pascalize:i,depascalize:o,camelizeKeys:function(d,g){return n(k(r,g),d)},decamelizeKeys:function(d,g){return n(k(o,g),d,g)},pascalizeKeys:function(d,g){return n(k(i,g),d)},depascalizeKeys:function(){return this.decamelizeKeys.apply(this,arguments)}};t.exports?t.exports=w:e.humps=w})(pr)})(nn);var hr=nn.exports,yr=["class","style"];function br(t){return t.split(";").map(function(e){return e.trim()}).filter(function(e){return e}).reduce(function(e,n){var a=n.indexOf(":"),r=hr.camelize(n.slice(0,a)),i=n.slice(a+1).trim();return e[r]=i,e},{})}function vr(t){return t.split(/\s+/).reduce(function(e,n){return e[n]=!0,e},{})}function an(t){var e=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},n=arguments.length>2&&arguments[2]!==void 0?arguments[2]:{};if(typeof t=="string")return t;var a=(t.children||[]).map(function(u){return an(u)}),r=Object.keys(t.attributes||{}).reduce(function(u,f){var m=t.attributes[f];switch(f){case"class":u.class=vr(m);break;case"style":u.style=br(m);break;default:u.attrs[f]=m}return u},{attrs:{},class:{},style:{}});n.class;var i=n.style,o=i===void 0?{}:i,s=gr(n,yr);return fn(t.tag,N(N(N({},e),{},{class:r.class,style:N(N({},r.style),o)},r.attrs),s),a)}var rn=!1;try{rn=!0}catch{}function xr(){if(!rn&&console&&typeof console.error=="function"){var t;(t=console).error.apply(t,arguments)}}function bt(t,e){return Array.isArray(e)&&e.length>0||!Array.isArray(e)&&e?O({},t,e):{}}function Ar(t){var e,n=(e={"fa-spin":t.spin,"fa-pulse":t.pulse,"fa-fw":t.fixedWidth,"fa-border":t.border,"fa-li":t.listItem,"fa-inverse":t.inverse,"fa-flip":t.flip===!0,"fa-flip-horizontal":t.flip==="horizontal"||t.flip==="both","fa-flip-vertical":t.flip==="vertical"||t.flip==="both"},O(O(O(O(O(O(O(O(O(O(e,"fa-".concat(t.size),t.size!==null),"fa-rotate-".concat(t.rotation),t.rotation!==null),"fa-pull-".concat(t.pull),t.pull!==null),"fa-swap-opacity",t.swapOpacity),"fa-bounce",t.bounce),"fa-shake",t.shake),"fa-beat",t.beat),"fa-fade",t.fade),"fa-beat-fade",t.beatFade),"fa-flash",t.flash),O(O(e,"fa-spin-pulse",t.spinPulse),"fa-spin-reverse",t.spinReverse));return Object.keys(n).map(function(a){return n[a]?a:null}).filter(function(a){return a})}function we(t){if(t&&st(t)==="object"&&t.prefix&&t.iconName&&t.icon)return t;if(Lt.icon)return Lt.icon(t);if(t===null)return null;if(st(t)==="object"&&t.prefix&&t.iconName)return t;if(Array.isArray(t)&&t.length===2)return{prefix:t[0],iconName:t[1]};if(typeof t=="string")return{prefix:"fas",iconName:t}}var Or=sn({name:"FontAwesomeIcon",props:{border:{type:Boolean,default:!1},fixedWidth:{type:Boolean,default:!1},flip:{type:[Boolean,String],default:!1,validator:function(e){return[!0,!1,"horizontal","vertical","both"].indexOf(e)>-1}},icon:{type:[Object,Array,String],required:!0},mask:{type:[Object,Array,String],default:null},maskId:{type:String,default:null},listItem:{type:Boolean,default:!1},pull:{type:String,default:null,validator:function(e){return["right","left"].indexOf(e)>-1}},pulse:{type:Boolean,default:!1},rotation:{type:[String,Number],default:null,validator:function(e){return[90,180,270].indexOf(Number.parseInt(e,10))>-1}},swapOpacity:{type:Boolean,default:!1},size:{type:String,default:null,validator:function(e){return["2xs","xs","sm","lg","xl","2xl","1x","2x","3x","4x","5x","6x","7x","8x","9x","10x"].indexOf(e)>-1}},spin:{type:Boolean,default:!1},transform:{type:[String,Object],default:null},symbol:{type:[Boolean,String],default:!1},title:{type:String,default:null},titleId:{type:String,default:null},inverse:{type:Boolean,default:!1},bounce:{type:Boolean,default:!1},shake:{type:Boolean,default:!1},beat:{type:Boolean,default:!1},fade:{type:Boolean,default:!1},beatFade:{type:Boolean,default:!1},flash:{type:Boolean,default:!1},spinPulse:{type:Boolean,default:!1},spinReverse:{type:Boolean,default:!1}},setup:function(e,n){var a=n.attrs,r=W(function(){return we(e.icon)}),i=W(function(){return bt("classes",Ar(e))}),o=W(function(){return bt("transform",typeof e.transform=="string"?Lt.transform(e.transform):e.transform)}),s=W(function(){return bt("mask",we(e.mask))}),u=W(function(){return cr(r.value,N(N(N(N({},i.value),o.value),s.value),{},{symbol:e.symbol,title:e.title,titleId:e.titleId,maskId:e.maskId}))});ln(u,function(m){if(!m)return xr("Could not find one or more icon(s)",r.value,s.value)},{immediate:!0});var f=W(function(){return u.value?an(u.value.abstract[0],{},a):null});return function(){return f.value}}});export{Or as F};
