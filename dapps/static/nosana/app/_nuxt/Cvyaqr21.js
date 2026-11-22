import{T as r,U as o}from"#entry";function u(){let e=0,t=!1;return r()&&o(()=>{t=!0,e+=1}),{begin:()=>++e,isCurrent:s=>!t&&s===e,cancel:()=>{e+=1}}}export{u};
