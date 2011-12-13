/* Implements user interaction.
   Currently it shows last 200 events for each log level due to browser limitations.
 */
LoggerApplication = function() {
  
  /*
  LogsState model stores:
  - tabs to display (log-levels)
  - number of events logged for each level    
  */
  this.LogsState = Backbone.Model.extend({
    MAP_LEVELS: {
        'crit': 'critical',
        'debg': 'debug',
        'warn': 'warning',
        'info': 'info',
        'other': 'other'
    },
    
    /*
    for each level corresponding section element stored in MAP_SECTIONS
    */
    MAP_SECTIONS: {}, // Will be initialized in constructor
      
    defaults: {
      show_critical: true,
	  show_warning:  true,
	  show_debug:    true,
	  show_info:     true,
      show_other:    true,
      count_critical: 0,
      count_warning:  0,
      count_debug:    0,
      count_info:     0,
      count_other:    0,
      console_show:   0, // 0 - disabled, 1 - show all, 2 - show checked for web-tabs
      socket:         null,
    },
    initialize: function() {
        var that = this;
        _.each(this.MAP_LEVELS, function(v, k) {
            that.MAP_SECTIONS[k] = $('section#logs-' + v);
        });
    },
    get_states: function() {
        /* Returns `active` states for each log-level */
        var result = {};
        var attributes = this.toJSON();
        _.each(attributes, function(v, k) {
           if (k.slice(0, 5) == 'show_') {
               result[k.slice(5, 20)] = v;
           }  
        });
        return result;
    },
    get_counts: function() {
        /* Returns number of log events for each log-level */
        var result = {};
        var attributes = this.toJSON();
        _.each(attributes, function(v, k) {
           if (k.slice(0, 6) == 'count_') {
               result[k.slice(6, 20)] = v;
           }  
        });
        return result;            
    },
    get_section: function(lvl) {
        /* returns section JQuery element by short level name */
        var section = this.MAP_SECTIONS[lvl];
        if (!section) {
            section = this.MAP_SECTIONS['other'];
        }
        return section;
    },
    handle_event: function(event) {
        /* Returns True, if web-based logger could handle event and increments 
           number of events for current log level.
           Returns False in case this log level is not checked to handle. */
        var result = false;
        var level = this.MAP_LEVELS[event.level];
        if (this.get('show_'+level)) {
            result = true;
            var o = {};
            o['count_'+level] = this.get('count_'+level)+1;
            this.set(o);
        }
        return result;
    },
    set_console_show: function(value) {
	    var obj = {'console_show': value};
	    this.set(obj); 
	    this.get('socket').emit('console_config', {show_console_log: value});      
    }
  });
  
  this.PreferencesView = Backbone.View.extend({
    /* Implements preferences panel view. */
	el: $("div#prefs"),
	
	events: {
		"click input:checkbox": "level_check",
		"click input:radio": "console_check"
	},
	
	initialize: function() {
	    /* Activates view refreshing on model data change. */
		this.model.bind('change', this.render, this);
	},
	level_check: function(e) {
	    /* Updates model with new state according to checked checkbox. */
	    var el = $(e.target);
	    var obj = {};
	    obj[el.attr('id')] = Boolean(el.attr('checked'));
		this.model.set(obj);
	},
	console_check: function(e) {
	    /* Updates model with console log configuration */
	    this.model.set_console_show($(e.target).val());
	},
	render: function() {
	    /* Renders view using model properties. */
	    var that = this;
	    _.each(this.model.get_states(), function(v, k) {
		    $("input#show_"+k, this.el).attr('checked', v);
	    });
	    $("input:radio").each(function() {
	        var el = $(this);
	        if (that.model.get('console_show') == el.val()) {
	            el.attr('checked', 'checked');
	        } else {
	            if (el.attr('checked')) {
	                el.removeAttr('checked');
                }
	        }
	    })
	}
  });

  this.TabsView = Backbone.View.extend({
    /* Implements tabs view. Number of events in tabs should be updated if logsState changes */
    el: $('nav#tabs'),
    
    initialize: function() {
        this.model.bind('change', this.render, this);
    },
    render: function() {
        var that = this;
        _.each(this.model.get_counts(), function(v, k) {
            var el = $("a[href='#"+k+"']", this.el).next();
            if (that.model.get('show_'+k)) {
                el.html('['+v+']');
            } else {
                el.html('');
            }
        });
    } 
  });
	
  this.Controller = Backbone.Router.extend({
    /* Setups routes: function routes, by accessing:
       - http://LOGMANAGER:PORT/#critical
       - http://LOGMANAGER:PORT/#debug
       - http://LOGMANAGER:PORT/#warning
       - http://LOGMANAGER:PORT/#info
       - http://LOGMANAGER:PORT/#other
       user gets to corresponding tab
    */
    routes: {
      ''         : 'index',
      ':type'    : 'logs'
    },
    render_template: $('#log_msg_template'),
    initialize: function(options) {
        this.logsState = options.logsState;
        this.logsState.change();
	},
    toggleNav: function(type) {
      $('nav#tabs li').removeClass('current');
      $('nav#tabs a[href="#'+type+'"]').parent().addClass('current');
    },
    hideAll: function() {
      /* Hides all sections. */
      $('div#log-output > section').removeClass('current');
    },
    index: function() {
      this.toggleNav('');
      this.hideAll();
      $('section#index').addClass('current');
    },
    logs: function(type) {
      /* Shows critical, debug, warning, info or other tab. */
      this.toggleNav(type);
      this.hideAll();
      $('section#logs-' + type).addClass('current');
    },
    new_event: function(event) {
      /* Log event processing method:
         - Checks, if log event should be shown
         - Creates new element (div - which copies form template div)
         - Updates corresponding elements with event data
         - Adds new event element to corresponding section (critical, warning, debug, info, other)
         - Deletes all extra elements so to keep max 100 events per tab.
      */
      if (this.logsState.handle_event(event)) {
          section = this.logsState.get_section(event.level);
          
          render_item = this.render_template.clone();
          render_item.removeClass('none').removeAttr('id');

          $('span.log_time', render_item).text(event.time)
          $('span.log_type', render_item).text(event.type)
          $('span.log_message', render_item).text(event.msg)

          section.prepend(render_item);
          while (section.children().length > 100) {
              section.children().last().remove();
          }
      }
    }
  });
  
  this.start = function() {
      /* Initializes controller, which processes tabs, socket.io client */
      var socket = io.connect('/');
      
      this.logsState   = new this.LogsState({socket: socket});
      this.preferences = new this.PreferencesView({ model: this.logsState });
      this.tabs        = new this.TabsView({ model: this.logsState })
      this.controller  = new this.Controller({ logsState: this.logsState });
      
      Backbone.history.start();

      if (typeof window !== 'undefined'){
          window.WEB_SOCKET_SWF_LOCATION = '/static/js/vendor/WebSocketMain.swf';
      }
  
      socket.on('log', function(event) {
          controller.new_event(event);
      });
  }
  
  return this;
}