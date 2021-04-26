
(function (factory) {
  // Making your jQuery plugin work better with npm tools
  // http://blog.npmjs.org/post/112712169830/making-your-jquery-plugin-work-better-with-npm
  if(typeof module === "object" && typeof module.exports === "object") {
    factory(require("jquery"), window, document);
  }
  else {
    factory(jQuery, window, document);
  }
}(function($, window, document, undefined) {

  var jqmodals = [],
      getCurrent = function() {
        return jqmodals.length ? jqmodals[jqmodals.length - 1] : null;
      },
      selectCurrent = function() {
        var i,
            selected = false;
        for (i=jqmodals.length-1; i>=0; i--) {
          if (jqmodals[i].$blocker) {
            jqmodals[i].$blocker.toggleClass('current',!selected).toggleClass('behind',selected);
            selected = true;
          }
        }
      };

  $.jqmodal = function(el, options) {
    var remove, target;
    this.$body = $('body');
    this.options = $.extend({}, $.jqmodal.defaults, options);
    this.options.doFade = !isNaN(parseInt(this.options.fadeDuration, 10));
    this.$blocker = null;
    if (this.options.closeExisting)
      while ($.jqmodal.isActive())
        $.jqmodal.close(); // Close any open jqmodals.
    jqmodals.push(this);
    if (el.is('a')) {
      target = el.attr('href');
      this.anchor = el;
      //Select element by id from href
      if (/^#/.test(target)) {
        this.$elm = $(target);
        if (this.$elm.length !== 1) return null;
        this.$body.append(this.$elm);
        this.open();
      //AJAX
      } else {
        this.$elm = $('<div>');
        this.$body.append(this.$elm);
        remove = function(event, jqmodal) { jqmodal.elm.remove(); };
        this.showSpinner();
        el.trigger($.jqmodal.AJAX_SEND);
        $.get(target).done(function(html) {
          if (!$.jqmodal.isActive()) return;
          el.trigger($.jqmodal.AJAX_SUCCESS);
          var current = getCurrent();
          current.$elm.empty().append(html).on($.jqmodal.CLOSE, remove);
          current.hideSpinner();
          current.open();
          el.trigger($.jqmodal.AJAX_COMPLETE);
        }).fail(function() {
          el.trigger($.jqmodal.AJAX_FAIL);
          var current = getCurrent();
          current.hideSpinner();
          jqmodals.pop(); // remove expected jqmodal from the list
          el.trigger($.jqmodal.AJAX_COMPLETE);
        });
      }
    } else {
      this.$elm = el;
      this.anchor = el;
      this.$body.append(this.$elm);
      this.open();
    }
  };

  $.jqmodal.prototype = {
    constructor: $.jqmodal,

    open: function() {
      var m = this;
      this.block();
      this.anchor.blur();
      if(this.options.doFade) {
        setTimeout(function() {
          m.show();
        }, this.options.fadeDuration * this.options.fadeDelay);
      } else {
        this.show();
      }
      $(document).off('keydown.jqmodal').on('keydown.jqmodal', function(event) {
        var current = getCurrent();
        if (event.which === 27 && current.options.escapeClose) current.close();
      });
      if (this.options.clickClose)
        this.$blocker.click(function(e) {
          if (e.target === this)
            $.jqmodal.close();
        });
    },

    close: function() {
      jqmodals.pop();
      this.unblock();
      this.hide();
      if (!$.jqmodal.isActive())
        $(document).off('keydown.jqmodal');
    },

    block: function() {
      this.$elm.trigger($.jqmodal.BEFORE_BLOCK, [this._ctx()]);
      this.$body.css('overflow','hidden');
      this.$blocker = $('<div class="' + this.options.blockerClass + ' blocker current"></div>').appendTo(this.$body);
      selectCurrent();
      if(this.options.doFade) {
        this.$blocker.css('opacity',0).animate({opacity: 1}, this.options.fadeDuration);
      }
      this.$elm.trigger($.jqmodal.BLOCK, [this._ctx()]);
    },

    unblock: function(now) {
      if (!now && this.options.doFade)
        this.$blocker.fadeOut(this.options.fadeDuration, this.unblock.bind(this,true));
      else {
        this.$blocker.children().appendTo(this.$body);
        this.$blocker.remove();
        this.$blocker = null;
        selectCurrent();
        if (!$.jqmodal.isActive())
          this.$body.css('overflow','');
      }
    },

    show: function() {
      this.$elm.trigger($.jqmodal.BEFORE_OPEN, [this._ctx()]);
      if (this.options.showClose) {
        this.closeButton = $('<a href="#close-jqmodal" rel="jqmodal:close" class="close-jqmodal ' + this.options.closeClass + '">' + this.options.closeText + '</a>');
        this.$elm.append(this.closeButton);
      }
      this.$elm.addClass(this.options.jqmodalClass).appendTo(this.$blocker);
      if(this.options.doFade) {
        this.$elm.css({opacity: 0, display: 'inline-block'}).animate({opacity: 1}, this.options.fadeDuration);
      } else {
        this.$elm.css('display', 'inline-block');
      }
      this.$elm.trigger($.jqmodal.OPEN, [this._ctx()]);
    },

    hide: function() {
      this.$elm.trigger($.jqmodal.BEFORE_CLOSE, [this._ctx()]);
      if (this.closeButton) this.closeButton.remove();
      var _this = this;
      if(this.options.doFade) {
        this.$elm.fadeOut(this.options.fadeDuration, function () {
          _this.$elm.trigger($.jqmodal.AFTER_CLOSE, [_this._ctx()]);
        });
      } else {
        this.$elm.hide(0, function () {
          _this.$elm.trigger($.jqmodal.AFTER_CLOSE, [_this._ctx()]);
        });
      }
      this.$elm.trigger($.jqmodal.CLOSE, [this._ctx()]);
    },

    showSpinner: function() {
      if (!this.options.showSpinner) return;
      this.spinner = this.spinner || $('<div class="' + this.options.jqmodalClass + '-spinner"></div>')
        .append(this.options.spinnerHtml);
      this.$body.append(this.spinner);
      this.spinner.show();
    },

    hideSpinner: function() {
      if (this.spinner) this.spinner.remove();
    },

    //Return context for custom events
    _ctx: function() {
      return { elm: this.$elm, $elm: this.$elm, $blocker: this.$blocker, options: this.options, $anchor: this.anchor };
    }
  };

  $.jqmodal.close = function(event) {
    if (!$.jqmodal.isActive()) return;
    if (event) event.preventDefault();
    var current = getCurrent();
    current.close();
    return current.$elm;
  };

  // Returns if there currently is an active jqmodal
  $.jqmodal.isActive = function () {
    return jqmodals.length > 0;
  };

  $.jqmodal.getCurrent = getCurrent;

  $.jqmodal.defaults = {
    closeExisting: true,
    escapeClose: true,
    clickClose: true,
    closeText: 'Close',
    closeClass: '',
    jqmodalClass: "jqmodal",
    blockerClass: "jquery-jqmodal",
    spinnerHtml: '<div class="rect1"></div><div class="rect2"></div><div class="rect3"></div><div class="rect4"></div>',
    showSpinner: true,
    showClose: true,
    fadeDuration: null,   // Number of milliseconds the fade animation takes.
    fadeDelay: 1.0        // Point during the overlay's fade-in that the jqmodal begins to fade in (.5 = 50%, 1.5 = 150%, etc.)
  };

  // Event constants
  $.jqmodal.BEFORE_BLOCK = 'jqmodal:before-block';
  $.jqmodal.BLOCK = 'jqmodal:block';
  $.jqmodal.BEFORE_OPEN = 'jqmodal:before-open';
  $.jqmodal.OPEN = 'jqmodal:open';
  $.jqmodal.BEFORE_CLOSE = 'jqmodal:before-close';
  $.jqmodal.CLOSE = 'jqmodal:close';
  $.jqmodal.AFTER_CLOSE = 'jqmodal:after-close';
  $.jqmodal.AJAX_SEND = 'jqmodal:ajax:send';
  $.jqmodal.AJAX_SUCCESS = 'jqmodal:ajax:success';
  $.jqmodal.AJAX_FAIL = 'jqmodal:ajax:fail';
  $.jqmodal.AJAX_COMPLETE = 'jqmodal:ajax:complete';

  $.fn.jqmodal = function(options){
    if (this.length === 1) {
      new $.jqmodal(this, options);
    }
    return this;
  };

  // Automatically bind links with rel="jqmodal:close" to, well, close the jqmodal.
  $(document).on('click.jqmodal', 'a[rel~="jqmodal:close"]', $.jqmodal.close);
  $(document).on('click.jqmodal', 'a[rel~="jqmodal:open"]', function(event) {
    event.preventDefault();
    $(this).jqmodal();
  });
}));
