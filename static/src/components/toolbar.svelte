<script lang="ts">

    let isVisible = false;
  
    function showToolbar() {
      isVisible = true;
    }
  
    function hideToolbar() {
      isVisible = false;
    }

    async function getIdea() {
    const requestBody: object = { title: 'New Idea', description: 'Idea Description' };
    const response = await fetch('http://localhost:5000/idea', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    const data = await response.json();
    console.log(data)
  }

  async function getSummary() {
    const requestBody: object = { title: 'New Idea', description: 'Idea Description' };
    const response = await fetch('http://localhost:5000/summarise', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    const data = await response.json();
    console.log(data)
  }
  </script>
  
  <!-- svelte-ignore a11y-mouse-events-have-key-events -->
  <div id="invisible-section" class="toolbar fixed right-0 top-0 h-2/3 w-12 opacity-5 z-50" on:mouseover={showToolbar} on:mouseleave={hideToolbar}></div>
   <!-- svelte-ignore a11y-mouse-events-have-key-events -->
  <div class="toolbar fixed right-0 top-0 h-2/3 w-20 bg-gray-500 z-50" on:mouseover={showToolbar} on:mouseleave={hideToolbar} style="{ isVisible ? 'transform: translateX(0);' : 'transform: translateX(12rem);' }">
    
    <ul class="flex flex-col items-center justify-center h-full">
      <li class="my-4">
        <!-- svelte-ignore a11y-invalid-attribute -->
        <a href="#" class="text-white hover:text-yellow-400" on:click={getIdea}><i class="fas fa-lightbulb"></i></a>
      </li>
      <li class="my-4">
        <a href="#" class="text-white hover:text-gray-200 hover:font-bold" on:click={getSummary}><i class="fas fa-list"></i></a>
      </li>
      <li class="my-4">
        <a href="#" class="text-white hover:text-blue-400"><i class="fas fa-save"></i></a>
      </li>
    </ul>
  </div>
  
  <style>
    .toolbar {
      transition: transform 0.2s ease-out;
    }
  
    .toolbar i {
      font-size: 1.5rem;
    }
  </style>
  