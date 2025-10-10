from crewai_local_project.crew import create_crew

def run():
    crew = create_crew()
    print("🚀 A equipe está pronta para começar a missão!")
    print("--------------------------------------------")
    result = crew.kickoff()

    print("\n\n##################################################")
    print("✅ Missão concluída! Aqui está o resultado final:")
    print("##################################################\n")
    print(result)

if __name__ == "__main__":
    run()