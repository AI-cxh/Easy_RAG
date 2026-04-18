import { computed, ref } from 'vue'
import { projectAPI, type Project } from '../api/client'

const projects = ref<Project[]>([])
const loading = ref(false)
const currentProjectIdState = ref<number | null>(
  Number(localStorage.getItem('current_project_id')) || null
)

function persistCurrentProject(projectId: number | null) {
  currentProjectIdState.value = projectId
  if (projectId) {
    localStorage.setItem('current_project_id', String(projectId))
  } else {
    localStorage.removeItem('current_project_id')
  }
}

export function useProject() {
  const currentProject = computed(() =>
    projects.value.find(project => project.id === currentProjectIdState.value) || null
  )

  const loadProjects = async () => {
    loading.value = true
    try {
      const result = await projectAPI.getList()
      projects.value = result.items || []
      if (!projects.value.length) {
        persistCurrentProject(null)
        return
      }

      const exists = projects.value.some(project => project.id === currentProjectIdState.value)
      if (!exists) {
        persistCurrentProject(projects.value[0].id)
      }
    } finally {
      loading.value = false
    }
  }

  const setCurrentProject = (projectId: number) => {
    persistCurrentProject(projectId)
  }

  const createProject = async (data: { name: string; description?: string }) => {
    const project = await projectAPI.create(data)
    projects.value = [project, ...projects.value]
    persistCurrentProject(project.id)
    return project
  }

  const updateProject = async (projectId: number, data: { name?: string; description?: string; visibility?: string }) => {
    const project = await projectAPI.update(projectId, data)
    const index = projects.value.findIndex(item => item.id === projectId)
    if (index !== -1) {
      projects.value[index] = project
    }
    return project
  }

  const deleteProject = async (projectId: number) => {
    await projectAPI.delete(projectId)
    projects.value = projects.value.filter(project => project.id !== projectId)
    if (currentProjectIdState.value === projectId) {
      persistCurrentProject(projects.value[0]?.id || null)
    }
  }

  return {
    projects,
    loading,
    currentProjectId: currentProjectIdState,
    currentProject,
    loadProjects,
    setCurrentProject,
    createProject,
    updateProject,
    deleteProject
  }
}
