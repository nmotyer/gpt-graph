<script>
    import { tweened } from 'svelte/motion';
    import { scale } from 'svelte/transition';
    import { cubicOut } from 'svelte/easing';
  
    let expanded = false;
    const size = tweened(24, {
		duration: 400,
		easing: cubicOut
	});
  
    function toggleExpanded() {
      expanded = !expanded;
      size.set($size == 24 ? 360 : 24);
    }
    /**
	 * @type {any[]}
	 */
     export let messages = [];
  
  </script>
  
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div class="flex flex-col items-center justify-center cursor-pointer w-full rounded-sm bg-gray-300 p-4"
  on:click={toggleExpanded}
  style="height: {$size}px;">
    <div class="w-full text-right"><div class="w-full"></div><p class="font-bold ">{expanded? 'close': 'see chat'}</p></div>
    {#if expanded}
      <div class="w-full h-auto max-h-72 rounded-sm bg-white mt-4 overflow-y-scroll p-4" id="chat-dialogue">
        {#each messages as message (message.id)}
          <p class=" {message.client? 'text-right font-bold': 'text-left'}">{message.content}</p><br />
        {/each}
      </div>
    {/if}
  </div>
  