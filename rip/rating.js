/* Copyright (C) 2007 - 2010 YOOtheme GmbH, YOOtheme License (http://www.yootheme.com/license) */
var Zoo = {};
Zoo.ElementRating=new Class({initialize:function(a,b){var c=this;this.url=b;this.div=$(a);this.div.getElement('input[name="reset-rating"]').addEvent("click",function(){c.resetVotes()})},resetVotes:function(){(new Ajax(this.url+"&task=callelement&method=reset",{method:"post",update:this.div})).request()}}); 
