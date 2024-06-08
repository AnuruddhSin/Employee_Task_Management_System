//sticky Navbar
const header = document.querySelector("header");
window.addEventListener("scroll",function() {
    header.classList.toggle("sticky",window.scrollY>100)
});
//toggle navbar
let menu = document.querySelector('#menu-icon');
let navlist = document.querySelector('.navlist');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
}
//scroll active
let section=document.querySelectorAll('section')
let navlink=document.querySelectorAll('header ul li a')
 window.onscroll=()=>{
    section.forEach(sec=>{
        let top=window.scrollY;
        let offset=sec.offsetTop-150;
        let height=sec.offsetHeight;
        let id=sec.getAttribute('id')
        if(top>offset && top<offset+height){
          navlink .forEach(links=>{
            links.classList.remove('active');
            document.querySelector('header ul li a[href*='+id+']').classList.add('active');
          });
        //animation on scroll
        sec.classList.add('show-animate');
        }
    });
    //remove toggle navbar
    menu.classList.remove('bx-x');
    navlist.classList.remove('open'); 
 }



 

