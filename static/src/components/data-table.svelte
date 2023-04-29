<script lang="ts">
    export let data: object[];
    import { scale, slide } from 'svelte/transition';

    let isTableCollapsed = false;
    let collapseIcon = '▲';

  function toggleTable() {
    isTableCollapsed = !isTableCollapsed;
    collapseIcon = isTableCollapsed ? '▼' : '▲';
  }
  </script>
  
  <table class="min-w-full divide-y divide-gray-200 mt-auto">
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <thead class="bg-gray-50  cursor-pointer" on:click={toggleTable}>
      <tr>
        {#each Object.keys(data[0]) as key}
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hover:bg-gray-200">
            {key}
          </th>
        {/each}
      </tr>
    </thead>
    {#if !isTableCollapsed}
    <tbody class="bg-white divide-y divide-gray-200" transition:slide>
      {#each data as row}
          <tr>
          {#each Object.values(row) as value}
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {value}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
    {/if}
  </table>
  
  <style>
    table {
      border-collapse: collapse;
    }
  
    th,
    td {
      border: 1px solid gray;
    }
  
    th {
      background-color: #f2f2f2;
      font-weight: bold;
    }
  
    td {
      padding: 0.5rem;
    }
  </style>
  